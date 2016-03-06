import sys
import logging

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


def main(args):
    if args[-1] == '-':
        ast = parse(sys.stdin.read())
    else:
        ast = parse(open(args[-1]).read())

    if args[0] == '--ast':
        log.info(ast)

    language = args[-2]

    if language == 'js':
        print(bootstrap_js())
        print(generate_js(ast))
    elif language == 'java':
        print(bootstrap_imports())
        print('public class Program {')
        print(bootstrap_java())
        print(generate_java(ast))
        print('public static void main(String[] args) { matcha_main(); }')
        print('}')
    else:
        print('unkonwn backend: %s' % language)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: main.py [ --ast ] <input>')
        sys.exit(1)

    main(sys.argv[1:])
