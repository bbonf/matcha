import logging
import os

from ..ast import (
    Assignment, BinaryOperator, Block, Function, IfStatement, Import,
    Invocation, ListLiteral, NumericLiteral, Return, StringLiteral,
    Symbol)
from ..ast.inference import (
    InferenceError, SymbolType, Types, infer, is_concrete_type, resolve_types)

log = logging.getLogger(__name__)

def join_arguments(args):
    out = []
    for arg in args:
        if type(arg) == str:
            out.append(arg)
        else:
            out.append(generate(arg))
    return ','.join(out)


def generate_type(typ):
    return {
        Types.Integer: 'int',
        Types.Double: 'double',
        Types.String: 'String',
        Types.List: 'List'
        }[typ]


def generate_block_symbols(node, exclude=()):
    infered_return, constrains = infer(node)
    resolved = resolve_types(constrains)

    local_symbols = []
    for t in resolved:
        if type(t) == SymbolType and not t.name in exclude:
            local_symbols.append('%s %s;' % (generate_type(resolved[t]), t.name))

    return '\n'.join(local_symbols)


def generate_function(node):
    body = generate_block(node.body)
    infered_return, constrains = infer(node)
    resolved = resolve_types(constrains)

    if not is_concrete_type(infered_return):
        infered_return = resolved[infered_return]

    return_type = generate_type(infered_return)

    args = {}
    for arg in node.args:
        found = False
        for constrain in constrains:
            if SymbolType(arg) in constrain:
                args[arg] = generate_type(resolved[SymbolType(arg)])
                found = True

        if not found:
            raise InferenceError('could not infer type of argument: %s' % arg)

    args_generated = []
    for arg, type_ in args.items():
        args_generated.append('%s %s' % (type_, arg))

    exclude_symbols = set([node.name]).union(args)
    return ('public static %s %s(%s) { %s\n%s };' %
            (return_type, node.name, join_arguments(args_generated),
                generate_block_symbols(node, exclude=exclude_symbols), body))


def generate_invocation(node):
    return ('%s(%s)' %
            (''.join(node.func), join_arguments(node.args)))


def generate_assignment(node):
    return ('%s = %s;' % (node.dst.name, generate(node.src)))


def generate_binary_operator(node):
    return ('(%s %s %s)' % (
        generate(node.first),
        node.operator,
        generate(node.second)))


def generate_if_statement(node):
    return ('if(%s) { %s }' % (generate(node.expression),
            generate_block(node.body)))


def generate_block(node):
    return ';'.join(generate(x) for x in node.body)


def generate_return(node):
    return 'return %s;' % generate(node.result)


def generate_string_literal(node):
    return '"' + node.value[1:-1]  + '"'


def generate_numeric_literal(node):
    return node.value


def generate_list_literal(node):
    return 'Arrays.asList(%s)' % (
        ','.join(map(generate, node.value)))


def generate_symbol(node):
    return node.name


def generate(node):
    generators = {
        Function: generate_function,
        Invocation: generate_invocation,
        Assignment: generate_assignment,
        BinaryOperator: generate_binary_operator,
        IfStatement: generate_if_statement,
        Block: generate_block,
        Return: generate_return,
        NumericLiteral: generate_numeric_literal,
        StringLiteral: generate_string_literal,
        ListLiteral: generate_list_literal,
        Symbol: generate_symbol,
        }

    try:
        return generators[type(node)](node)
    except KeyError:
        raise RuntimeError('unknown node: %r' % (node,))


def generate_program(ast):
    definitions = []
    main = []

    for node in ast.body:
        if type(node) == Function:
            definitions.append(node)
        elif type(node) != Import:
            main.append(node)

    symbols = ''.join(generate_block_symbols(m) for m in main)

    return '\n'.join(generate(d) for d in definitions) + \
        'public static void matcha_main() { %s\n%s; }' % \
        (symbols, ';\n'.join(generate(x) for x in main))


def bootstrap():
    with open(os.path.join(os.path.dirname(__file__), 'bootstrap.java')) as f:
        return f.read()

def bootstrap_imports():
    return '\n'.join(
        'import %s;' % package for package in [
            'java.util.List',
            'java.util.Arrays',
            'java.util.stream.Collectors'])
