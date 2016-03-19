import sys
import logging
import os

from matcha.ast import get_imports
from matcha.parsing import program
from matcha.js import generate as generate_js
from matcha.java import bootstrap_imports
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


def std_lookup(module_name, language):
    possible = [
        '%s.%s' % (module_name, 'tea'),
        '%s.%s' % (module_name, language)]

    std_path = os.getenv('MATCHA_LIB', 'matcha/std')
    return [os.path.join(std_path, p)
            for p in possible]


def module_lookup(module_name, parent_path, language):
    for filename in std_lookup(module_name, language):
        if os.path.exists(filename):
            return filename, True

    possible = (
        parent_path,
        os.getcwd())

    possible = [os.path.join(
        p, '%s.%s' % (module_name, 'tea'))
        for p in possible]

    for filename in possible:
        if os.path.exists(filename):
            return filename, False

    return None, False

def should_compile(source):
    return source.endswith('.tea')


def compile_module(out, module_name, ast, language, is_main=False):
    if language == 'js':
        out.write(generate_js(ast))
    elif language == 'java':
        out.write(bootstrap_imports())
        out.write('public class %s {' % module_name)
        if is_main:
            out.write('public static void main(String[] args) { matcha_main(); }')
        out.write(generate_java(ast))
        out.write('}')
    else:
        raise RuntimeError('Unknown backend: %s' % language)

def link_module(filename, module_name, language, is_std=False):
    if language == 'java':
        if is_std:
            sys.stdout.write('import matcha.std.%s;' % module_name)
    else:
        sys.stdout.write('var %s = (function(){' % module_name);
        sys.stdout.write(open(filename).read())
        sys.stdout.write('return exports;})();')

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
        module_name = import_.name
        filename, is_std = module_lookup(
            module_name,
            os.path.dirname(args[-1]),
            language)

        if not filename:
            raise RuntimeError('could not find module: %s' % module_name)

        if should_compile(filename):
            module_ast = parse(open(filename).read())

            output_filename = '%s.%s' % (module_name, language)
            with open(output_filename, 'w') as out:
                compile_module(out, module_name, module_ast, language)

            link_module(output_filename, module_name, language)
        else:
            link_module(filename, module_name, language, is_std=True)

    compile_module(sys.stdout, 'Program', ast, language, is_main=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: main.py [ --ast ] <input>')
        sys.exit(1)

    main(sys.argv[1:])
