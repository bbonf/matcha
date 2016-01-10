import sys
import logging

from matcha.parsing import program
from matcha.js import bootstrap, generate

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
    ast = parse(open(args[-1]).read())
    if args[0] == '--ast':
        log.info(ast)

    print(bootstrap())
    print(generate(ast))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: main.py [ --ast ] <input>')
        sys.exit(1)

    main(sys.argv[1:])

