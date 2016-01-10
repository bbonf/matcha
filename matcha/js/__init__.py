import os

from ..ast import (Function, Invocation, Assignment, BinaryOperator,
    IfStatement, Block, Return, Literal, Symbol)

def join_arguments(args):
    out = []
    for arg in args:
        if type(arg) == str:
            out.append(arg)
        else:
            out.append(generate(arg))
    return ','.join(out)

def generate_function(node):
    body = generate_block(node.body)
    return ('var %s = function(%s) { %s };' %
        (node.name, join_arguments(node.args), body))

def generate_invocation(node):
    return ('%s(%s)' %
        (''.join(node.func), join_arguments(node.args)))

def generate_assignment(node):
    return ('%s = %s;' % (node.dst, generate(node.src)))

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
        Symbol: generate_symbol,
        }

    try:
        return generators[type(node)](node)
    except KeyError:
        raise RuntimeError('unknown node: %r' % (node,))


def bootstrap():
    with open(os.path.join(os.path.dirname(__file__), 'bootstrap.js')) as f:
        return f.read()
