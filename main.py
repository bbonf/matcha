import sys
import logging
import os

from matcha.ast import get_imports
from matcha.parsing import program
from matcha.js import bootstrap as bootstrap_js
from matcha.js import generate as generate_js
from matcha.java import bootstrap as bootstrap_java, bootstrap_imports
from matcha.java import generate_program as generate_java

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def parse(text):
    result = program()(text)
    if not result:
        log.critical('failed parsing')
        return

    ast, rest = result
    if rest:
        log.critical('failed parsing, leftover: %s', rest)
        log.critical(ast)
        return

    return ast


def module_lookup(module_name, parent_path):
    possible = (
        parent_path,
        os.getcwd())

    return (os.path.join(
        p, '%s.%s' % (module_name, 'tea'))
        for p in possible)


def compile_module(out, module_name, ast, language, is_main=False):
    if language == 'js':
        out.write(bootstrap_js())
        out.write(generate_js(ast))
    elif language == 'java':
        out.write(bootstrap_imports())
        out.write('public class %s {' % module_name)
        if is_main:
            out.write('public static void main(String[] args) { matcha_main(); }')
        out.write(bootstrap_java())
        out.write(generate_java(ast))
        out.write('}')
    else:
        raise RuntimeError('Unknown backend: %s' % language)


def main(args):
    if args[-1] == '-':
        ast = parse(sys.stdin.read())
    else:
        ast = parse(open(args[-1]).read())

    if args[0] == '--ast':
        print(ast)

    language = args[-2]

    imports = get_imports(ast.body)
    for import_ in imports:
        module_ast = None
        for filename in module_lookup(import_.name, os.path.dirname(args[-1])):
            if os.path.exists(filename):
                module_ast = parse(open(filename).read())

        if not module_ast:
            print('could not find module')
            sys.exit(1)

        module_name = import_.name
        output_filename = '%s.%s' % (module_name, language)
        with open(output_filename, 'w') as out:
            compile_module(out, module_name, module_ast, language)

    compile_module(sys.stdout, 'Program', ast, language, is_main=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: main.py [ --ast ] <input>')
        sys.exit(1)

    main(sys.argv[1:])
