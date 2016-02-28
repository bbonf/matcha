import os

from ..ast import (Assignment, BinaryOperator, Block, Function, IfStatement,
   Invocation, Literal, Return, Symbol, ListLiteral)
from ..ast.inference import infer, SymbolType, resolve_types, is_concrete_type, InferenceError


def join_arguments(args):
    out = []
    for arg in args:
        if type(arg) == str:
            out.append(arg)
        else:
            out.append(generate(arg))
    return ','.join(out)


def generate_block_symbols(node, exclude=()):
    infered_return, constrains = infer(node)
    resolved = resolve_types(constrains)

    local_symbols = []
    for t in resolved:
        if type(t) == SymbolType and not t.name in exclude:
            local_symbols.append('var %s;' % t.name)

    return '\n'.join(local_symbols)


def generate_function(node):
    body = generate_block(node.body)
    infered_return, constrains = infer(node)
    resolved = resolve_types(constrains)

    if not is_concrete_type(infered_return):
        infered_return = resolved[infered_return]

    args = {}
    for arg in node.args:
        found = False
        for constrain in constrains:
            if SymbolType(arg) in constrain:
                args[arg] = resolved[SymbolType(arg)]
                found = True

        if not found:
            raise InferenceError('could not infer type of argument: %s' % arg)

    args_generated = []
    for arg, type_ in args.items():
        args_generated.append('%s %s' % (type_, arg))

    exclude_symbols = set([node.name]).union(args)
    return ('var %s = function(%s) { %s\n%s };' %
            (node.name, join_arguments(node.args),
                generate_block_symbols(node, exclude=exclude_symbols), body))


def generate_invocation(node):
    return ('%s(%s)' %
            (''.join(node.func), join_arguments(node.args)))


def generate_assignment(node):
    assert type(node.dst) == Symbol

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
    return 'return %s' % generate(node.result)


def generate_literal(node):
    return node.value


def generate_list_literal(node):
    return '[%s]' % ','.join(generate(x) for x in node.value)


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
        Literal: generate_literal,
        ListLiteral: generate_list_literal,
        Symbol: generate_symbol,
        }

    try:
        return generators[type(node)](node)
    except KeyError:
        raise RuntimeError('unknown node: %r' % (node,))


def bootstrap():
    with open(os.path.join(os.path.dirname(__file__), 'bootstrap.js')) as f:
        return f.read()
