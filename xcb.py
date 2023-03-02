#!/usr/bin/env python3
#
# Tokens:
#   - Text
#   - #name
#   - ## comment
#   - #{ open code
#   - }# close code
#   - #( open directive
#   - ) close directive
#   - ident
#   - ( open paren
#   - ) close paren
#   - [ open bracket
#   - ] close bracket
#   - { open brace
#   - } close brace
#   - : colon
#   - ; semicolon
#   - , comma
#   - = equals

from enum import Enum

class TokenKind(Enum):
    TEXT = 0
    COMMENT = 1
    CODE = 2
    START_DIRECTIVE = 3
    END_DIRECTIVE = 4
    IDENT = 5
    NAME = 6
    OPEN_PAREN = 7
    CLOSE_PAREN = 8
    OTHER = 9
    COMMA = 10
    DOLLAR = 11

class Token:
    def __init__(self, kind: TokenKind, value: str):
        self.kind = kind
        self.value = value


def is_name_char(s: str) -> bool:
    return not s is None and (s.isalpha() or s == "_")

class CharReader:
    pos = 0

    def __init__(self, text: str):
        self.text = text

    def eof(self) -> bool:
        self.pos >= len(self.text)

    def peek(self, offset=None) -> str:
        if offset is None:
            offset = 0
        if self.pos + offset >= len(self.text):
            return None
        return self.text[self.pos + offset]
    
    def next(self, n= None) -> str:
        if n is None:
            n = 1
        c = self.peek()
        self.pos += 1
        return c
    
class Lexer:
    def __init__(self, s: str):
        self.reader = CharReader(s)
        self.buffer = ""
        self.tokens = []

    def token(self, kind: TokenKind):
        if len(self.buffer.strip()) > 0:
            token = Token(kind, self.buffer)
            self.tokens.append(token)
        self.buffer = ""

    def lex(self):
        while c := self.reader.peek():
            if c == '#':
                c2 = self.reader.peek(1)
                self.token(TokenKind.TEXT)
                if c2 == '#':
                    self.lex_comment()
                elif c2 == '{':
                    self.lex_code()
                elif c2 == '(': 
                    self.lex_directive()
                else:
                    self.lex_name()
            
            else:
                self.next()

        self.token(TokenKind.TEXT)

    def lex_comment(self):
        while self.next() != '\n':
            pass

        self.token(TokenKind.COMMENT)

    def lex_code(self):
        while not self.reader.eof():
            c = self.next()

            if c == '}':
                c2 = self.reader.peek()
                if c2 == '#':
                    self.next()
                    break

        self.token(TokenKind.CODE)

    def lex_directive(self):
        self.next()
        self.next()
        self.token(TokenKind.START_DIRECTIVE)

        indent = 1

        while not self.reader.eof():
            match self.next():
                case ')':
                    if indent == 1:
                        break

                    indent -= 1
                    self.token(TokenKind.CLOSE_PAREN)
                case '(':
                    indent += 1
                    self.token(TokenKind.OPEN_PAREN)
                case ',':
                    self.token(TokenKind.COMMA)
                case '$':
                    self.token(TokenKind.DOLLAR)
                case c:
                    if is_name_char(c):
                        self.lex_ident()
                    else:
                        self.lex_other()

        self.token(TokenKind.END_DIRECTIVE)

    def lex_other(self):
        while c := self.reader.peek():
            if is_name_char(c):
                break
            if c == '(' or c == ')' or c == ',' or c == '$':
                break
            self.next()

        self.token(TokenKind.OTHER)

    def lex_ident(self):
        while is_name_char(self.reader.peek()):
            self.next()

        self.token(TokenKind.IDENT)

    def lex_name(self):
        self.next()

        while is_name_char(self.reader.peek()):
            self.next()

        self.token(TokenKind.NAME)

    def next(self) -> str:
        if n := self.reader.next():
            self.buffer += n
            return n
        return None

# Now, we create logical structures
class Item:
    pass

class Text(Item):
    def __init__(self, value: str):
        self.value = value

class Code(Item):
    def __init__(self, value: str):
        self.value = value

class Name(Item):
    def __init__(self, value: str):
        self.value = value

# We can ignore comments

class Directive(Item):
    def __init__(self, name: str, args: list[Token]):
        self.name = name
        self.args = args

class BlockDirective(Directive):
    def __init__(self, name: str, args: list[Token], items: list[Item]):
        super().__init__(name, args)
        self.items = items

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> list[Item]:
        items = []

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.kind == TokenKind.TEXT:
                items.append(Text(token.value))
            elif token.kind == TokenKind.CODE:
                items.append(Code(token.value[2:-2]))
            elif token.kind == TokenKind.NAME:
                items.append(Name(token.value[1:]))
            elif token.kind == TokenKind.START_DIRECTIVE:
                items.append(self.parse_directive())
            else:
                print("unexpected token: " + token.value + "")

            self.pos += 1

        return items

    def parse_directive(self):
        self.pos += 1
        name = self.tokens[self.pos].value
        self.pos += 1
        args = []

        while self.tokens[self.pos].kind != TokenKind.END_DIRECTIVE:
            token = self.tokens[self.pos]

            args.append(token)

            self.pos += 1

        return Directive(name, args)
    
blocks = [ 'if', 'for', 'macro' ]

class Analyzer:
    def __init__(self, items: list[Item]):
        self.items = items
        self.pos = 0

    def analyze(self) -> list[Item]:
        output = []

        while self.pos < len(self.items):
            item = self.items[self.pos]

            self.pos += 1

            if isinstance(item, Directive):
                output.append(self.analyze_directive(item))
            else:
                output.append(item)

        return output

    def analyze_directive(self, item: Directive):
        block_name = item.name
        args = item.args

        if not block_name in blocks:
            return item

        block = []

        while self.pos < len(self.items):
            item = self.items[self.pos]

            self.pos += 1

            if isinstance(item, Directive):
                if item.name == 'end' and len(item.args) > 0 and item.args[0].value == block_name:
                    break
                block.append(self.analyze_directive(item))
            else:
                block.append(item)

        return BlockDirective(block_name, args, block)
    
class Macro:
    def __init__(self, name: str, args: list[str], content: list[Item]):
        self.name = name
        self.args = args
        self.content = content

def unindent(s: str) -> str:
    with_spaces = s.replace('\t', '    ')
    lines = with_spaces.split('\n')

    indent = min([ len(line) - len(line.lstrip(' ')) for line in lines if line.strip() != '' ])

    unindented_lines = []

    for line in lines:
        leading = len(line) - len(line.lstrip())
        offset = min(leading, indent)

        unindented_lines.append(line[offset:])

    return '\n'.join(unindented_lines)
    
class Concretizer:
    def __init__(self, items: list[Item]):
        self.items = items
        self.macros = dict()
        self.buffer = ""

    def concretize(self):
        globals = dict()

        self.eval(self.items, globals)

    def print(self, s):
        self.buffer += str(s)


    def eval(self, items: list[Item], globals):
        for item in items:
            if isinstance(item, Text):
                self.print(item.value)
            elif isinstance(item, Name):
                code = unindent(item.value)
                #try:
                self.print(eval(code, globals))
                #except Exception as e:
                #    print(e)
            elif isinstance(item, Code):
                #try:
                code = unindent(item.value)
                exec(code, globals)
                #except Exception as e:
                #    print(e)
            elif isinstance(item, BlockDirective):
                match item.name:
                    case "if":
                        predicate = unindent("".join([item.value for item in item.args]))
                        #try:
                        is_true = eval(predicate, globals)

                        if is_true:
                            self.eval(item.items, globals)
                        #except Exception as e:
                        #    pass
                    case "for":
                        name = item.args[0].value

                        if item.args[1].value != "in":
                            print("error: expected 'in'")

                        params_code = unindent("".join([item.args[i].value for i in range(2, len(item.args))]))
                        params = eval(params_code, globals)

                        old = None
                        if name in globals:
                            old = globals[name]

                        for i in params:
                            globals[name] = i
                            self.eval(item.items, globals)

                        if old is None:
                            del globals[name]
                        else:
                            globals[name] = old
                    
                    case "macro":
                        macro_name = item.args[0].value

                        params = []

                        if len(item.args) > 1:
                            if item.args[1].value != "(":
                                print("error: expected '('")

                            i = 2

                            while i < len(item.args) and item.args[i].value != ")":
                                if item.args[i].value.strip() != ",":
                                    params.append(item.args[i].value)

                                i += 1

                        macro = Macro(macro_name, params, item.items)

                        self.macros[macro_name] = macro
            elif isinstance(item, Directive):
                if item.name in self.macros:
                    self.expand_macro(self.macros[item.name], item.args, globals)
                match item.name:
                    case '$':
                        if len(item.args) == 0:
                            return
                        code = ''.join([i.value for i in item.args])

                        self.print(eval(code, globals))

    def expand_macro(self, macro: Macro, args_list: list[Token], globals):
        args = Concretizer.get_args(args_list)

        if len(args) != len(macro.args):
            print("error: wrong number of arguments for macro '" + macro.name + "'")

        old_args = {}

        for arg in macro.args:
            if arg in globals:
                old_args[arg] = globals[arg]
            else:
                old_args[arg] = None

        for i in range(len(args)):
            globals[macro.args[i]] = eval(unindent(args[i]), globals)

        self.eval(macro.content, globals)

        for arg in macro.args:
            if old_args[arg] is None:
                del globals[arg]
            else:
                globals[arg] = old_args[arg]

    def get_args(args_list: list[Token]) -> list[str]:
        args = []

        if len(args_list) == 0:
            return []
        
        if args_list[0].value != "(":
            print("error: expected '('")
            return []
        
        i = 1

        arg = ""
        
        while i < len(args_list) and args_list[i].value != ")":
            if args_list[i].value == ",":
                args.append(arg)
                arg = ""
            else:
                arg += args_list[i].value
            
            i += 1

        args.append(arg)
        
        return args

import sys

filename = "macro.txt.xcb"
if len(sys.argv) > 1:
    filename = sys.argv[1]
file = open(filename, 'r')
text = file.read()
lexer = Lexer(text)
lexer.lex()

tokens = lexer.tokens
parser = Parser(tokens)
analyzer = Analyzer(parser.parse())
concretizer = Concretizer(analyzer.analyze())
concretizer.concretize()
print(concretizer.buffer)

def print_item(item: Item, indent: int = 0):
    mindent = " " * indent
    if isinstance(item, Text):
        print (f"{mindent}text '{item.value}'")
    elif isinstance(item, Name):
        print(f"{mindent}name {item.value}")
    elif isinstance(item, Code):
        print(f"{mindent}code {item.value}")
    elif isinstance(item, BlockDirective):
        block_name = item.name
        print(f"{mindent}block {block_name}")
        for item in item.items:
            print_item(item, indent + 4)
        print(f"{mindent}end {block_name}")
    elif isinstance(item, Directive):
        print(f"{mindent}directive {item.name}")
        for arg in item.args:
            print(f"{mindent}{arg.value}")

for item in analyzer.analyze():
    print_item(item)