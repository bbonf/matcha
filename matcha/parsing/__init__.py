from .base import (then, either, many, p_regex, match,
    strip, rstrip, joined, joined_skip, flat, wrapped, then_all, ParsingException,
    oneof)
from ..ast import (Function, Invocation, Assignment, BinaryOperator,
    IfStatement, Block, Return, NumericLiteral, StringLiteral,
    ListLiteral, Symbol)

import logging
log = logging.getLogger(__name__)

def trace(p):
    def t(text):
        print('>>>>>', text.replace(' ','[ ]').replace('\n','\\n'))
        return p(text)

    return t

def dbg(p):
    return p

class Parser:
    def __init__(self, func, node):
        self.func = func
        self.node = node

    def __call__(self, *args):
        try:
            result = self.func(*args)
        except ParsingException as e:
            log.error('syntax error, expected %s, got: %s' %
                (e.expected, e.rest))
            log.error('parser is: %s', e.parser)
            return None

        if not result:
            #raise RuntimeError('could not parse %s' % self.node)
            return None

        if type(result[0]) == dict:
            return self.node(**result[0]), result[1]

        return self.node(result[0]), result[1]


def empty_line():
    return p_regex('\\s*\n')

def symbol():
    return rstrip(p_regex('[a-zA-Z_]+[a-zA-Z_\\d]*'))

def free_symbol():
    return strip(p_regex('[a-zA-Z_]+[a-zA-Z_\\d]*'))

def dotted_name():
    return Parser(
        flat(joined(match('.'), symbol())),
        Symbol)

def string_literal():
    return either(p_regex('".*?"'), p_regex("'.*?'"))

def numeric_literal():
    return p_regex(r'\d+(\.\d*)?')

def list_literal():
    return wrapped(
        match('['),
        joined_skip(match(','), strip(expression())),
        match(']'))

def literal():
    return either(
            Parser(string_literal(), StringLiteral),
            Parser(numeric_literal(), NumericLiteral),
            Parser(list_literal(), ListLiteral))

def atom():
    return rstrip(either(dotted_name(), literal()))

def free_atom():
    return strip(either(dotted_name(), literal()))

def indent(p):
    def indent_parser(text):
        split = text.split('\n')
        matched = []
        for i in range(len(split)):
            line = split[i]
            if line.startswith('    '):
                matched.append(line[4:])
            elif line:
                # stop on the first non-empty line that's
                # not properly indented
                i -= 1
                break

        rest = '\n'.join(split[i+1:])
        if matched:
            r = p('\n'.join(matched))
            return r[0], r[1] + rest

        return None

    return indent_parser

def arguments():
    return wrapped(
        match('('),
        joined_skip(match(','), free_symbol()),
        match(')'))

def invocation_arguments():
    return wrapped(
        match('('),
        joined_skip(match(','), strip(expression())),
        match(')'))

def invocation():
    return Parser(then(
        'func', dotted_name(),
        'args', invocation_arguments()), Invocation)

def placeholder(f, z):
    memo = {}
    def load(*args):
        return memo.setdefault((f,z), f(*z))(*args)

    return load

def memoize(f):
    def helper(*args):
        return placeholder(f, args)
    return helper

@memoize
def binary_operator():
    return Parser(then(
        'first', either(invocation(), atom()),
        'operator', strip(oneof([
            '+','-','*','/',
            '==','!=', '>', '<'])),
        'second', expression()), BinaryOperator)

@memoize
def expression():
    return either(
        binary_operator(),
        invocation(),
        atom())


def end_def():
    return match(':\n')

def if_statement():
    return Parser(then(
        '_', match('if '),
        'expression', expression(),
        '_', end_def(),
        'body', block()), IfStatement)

def assignment():
    return Parser(then(
        'dst', Parser(symbol(), Symbol),
        '_', rstrip(match('=')),
        'src', atom()), Assignment)

def return_statement():
    return Parser(then(
        '_', match('return '),
        'result', expression()), Return)

@memoize
def statement():
    return either(invocation(), assignment(),
        if_statement(), return_statement())


def block():
    return Parser(
        then(
            'body', indent(many(
                rstrip(statement()))))
        , Block)

def function(level):
    return Parser(then_all(
            '_', match('def '),
            'name', symbol(),
            'args', arguments(),
            '_', end_def(),
            'body', block()), Function)

def definition(level=0):
    return either(function(level))

def program():
    return Parser(
        then(
            'body',
            many(rstrip(either(empty_line(), definition(), statement())))),
        Block)
