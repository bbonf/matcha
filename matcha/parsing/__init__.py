from .base import (then, either, many, p_regex, match,
    strip, rstrip, joined, joined_skip, flat, wrapped, then_all, ParsingException,
    oneof)
from ..ast import Function, Invocation, Assignment

import logging
log = logging.getLogger(__name__)

def trace(p):
    def t(text):
        print('>>>>>', text.replace(' ','[ ]').replace('\n','\\n'))
        return p(text)

    return t

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
        return self.node(**result[0]), result[1]


def empty_line():
    return p_regex('\\s*\n')

def symbol():
    return rstrip(p_regex('[a-zA-Z_]+[a-zA-Z_\\d]*'))

def free_symbol():
    return strip(p_regex('[a-zA-Z_]+[a-zA-Z_\\d]*'))

def dotted_name():
    #return many_flat(either(symbol(), match('.')))
    return flat(joined(match('.'), symbol()))

def string_literal():
    return either(p_regex('".*"'), p_regex("'.*'"))

def numeric_literal():
    return p_regex(r'\d+')

def literal():
    return either(string_literal(), numeric_literal())

def atom():
    return rstrip(either(dotted_name(), literal()))

def free_atom():
    return strip(either(dotted_name(), literal()))

def indent():
    return match('    ')

def arguments():
    return wrapped(
        match('('),
        joined_skip(match(','), free_symbol()),
        match(')'))

def invocation_arguments():
    return wrapped(
        match('('),
        joined_skip(match(','), free_atom()),
        match(')'))

def invocation():
    return Parser(then(
        'func', dotted_name(),
        'args', invocation_arguments()), Invocation)

def binary_operator():
    return then(
        'first', atom(),
        'operator', oneof([
            '+','-','*','/',
            '==','!=']),
        'second', atom())

def expression():
    return either(
        atom(),
        invocation(),
        binary_operator())

def assignment():
    return Parser(then(
        'dst', symbol(),
        '_', rstrip(match('=')),
        'src', atom()), Assignment)

def statement():
    return either(invocation(), assignment())

def block(level):
    return many(
        either(empty_line(),
            wrapped(
                match('    ' * level),
                statement(),
                either(match('\n'), match('')))))


def function(level):
    return Parser(then_all(
            '_', match('def '),
            'name', symbol(),
            'args', arguments(),
            '_', match(':\n'),
            'body', block(level+1)), Function)

def definition(level=0):
    return either(function(level))

def program():
    return many(either(definition(), statement()))
