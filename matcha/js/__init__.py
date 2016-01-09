import os
from functools import partial

from ..ast import Function, Invocation, Assignment

def join_arguments(args):
    return ','.join(args)

def generate_function(node):
    body = ''.join(generate()(node.body))
    return ('var %s = function(%s) { %s };' %
        (node.name, join_arguments(node.args), body))

def generate_invocation(node):
    return ('%s(%s);' %
        (''.join(node.func), join_arguments(node.args)))

def generate_assignment(node):
    return ('%s = %s;' % (node.dst, node.src))


def generate():
    def g(node):
        generators = {
            Function: generate_function,
            Invocation: generate_invocation,
            Assignment: generate_assignment,
            }

        try:
            return generators[type(node)](node)
        except KeyError:
            raise RuntimeError('unknown node: %r' % (node,))

    return partial(map, g)


def bootstrap():
    with open(os.path.join(os.path.dirname(__file__), 'bootstrap.js')) as f:
        return f.read()
