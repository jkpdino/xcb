#!/usr/bin/env python3
from pathlib import Path
import subprocess

def fail_test(test, expected, actual):
    print(f"[x] {test}")

    error_path = test + '.err'

    with open(error_path, 'w') as f:
        f.write("==== Expected ====\n")
        f.write(expected)
        f.write("==================\n")

        f.write("==== Actual ======\n")
        f.write(actual)
        f.write("==================\n")


def pass_test(test):
    print(f"[ ] {test}")


tests = [str(x) for x in Path('.').rglob('*.xcb')]

for test in tests:
    reduced = subprocess.check_output(['./xcb.py', test]).decode('utf-8')

    expected_path = test[:-4]

    with open(expected_path, 'r') as f:
        expected = f.read()

        if reduced == expected:
            pass_test(expected_path)
        else:
            fail_test(expected_path, expected, reduced)


