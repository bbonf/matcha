from matcha.parsing import program
from matcha.js import bootstrap, generate

def parse(text):
    return program()(text)

def compile():
    parsed = parse(
    'def hello(a,b):\n'
    '    sys.log("hello")\n'
    '    bar = 5\n'
    '\n\n'
    'hello(1, 2)'
    )

    ast, rest = parsed
    if rest:
        print('failed parsing, leftover:', rest)
        print(ast)
        return

    out = generate()(ast)
    print('\n'.join(out))

if __name__ == '__main__':
    print(bootstrap())
    compile()

