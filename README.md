# XCB

XCB stands for eXpand Code Boilerplate. XCB allows for powerful metaprogramming through variables, macros, if and for directives, and built-in python code. XCB can be considered a code pre-processor.

## Items

### Name

Typing `#name` anywhere in a file will expand into the variable `name`

### Text

Any text entered will display as itself.

### Code

A code block will execute arbitrary python code. Code blocks have their tabs transformed into 4 spaces, and are automatically unindented by the lowest non-empty line's spaces. A code block starts with `#{` and ends with `}#`.

### Comments

Any comment line is ignored. A comment line starts with `##`.

### Directive

A directive starts with a `#(` and ends with `)`. Nested parenthesis are allowed within a directive. The first word within a directive is its function, and the rest of it is arguments. Directives are used for macros, evaluation, and if and for directives.

## Directives

### Eval

The `$` directive evaluates any code placed after it. This is useful when a variable expansion needs to be part of a word, or when evaluating an expression.

### Define

The `define` directive defines a variable. The first argument will be the variable name, and anything after that will be evaluated as its value.

### Block directives

Some directives are implemented as blocks. A block contains all content from the opening directive to the closing directive. The closing directive is of the form `#(end ...)`, where ... is the opening directive function. For example, a macro would be ended by `#(end macro)`

### If

An if directive only displays its contents if its condition evaluates to true. An if directive is written `#(if *condition*)` and ends with `#(end if)`.

### For

A for directive repeats its contents a number of times, with a variable set to an item of an iterator each time. A for directive is written `#(for *variable* in *iterator*)` and ends with `#(end for)`.

### Macros

A macro defines a reusable piece of code that can be parameterized. A macro is defined by `#(macro *macro_name* (*parameters*)?)`, and ends with `#(end macro)`. Anything in between is evaluated as the macros content. A macro takes named parameters that can be used like regular variables in its invokation.

A macro can be instantiated by using a directive with the function of the macro name


## Warning

This is not at all stable.