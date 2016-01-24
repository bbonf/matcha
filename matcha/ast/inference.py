from collections import namedtuple
from enum import Enum
from itertools import filterfalse

from . import (Function, Literal, Return, IfStatement, Invocation, Assignment,
    Symbol, BinaryOperator, Block)

Types = Enum('Types', 'Integer, Double, String')
SymbolType = namedtuple('SymbolType', 'name')

class InferenceError(Exception):
    pass


def flatten(lst):
    if type(lst) == list:
        return reduce(lambda x, y: x+y, (map(flatten, lst)))

    # also filters None
    if lst:
        return [lst]
    return []


def infer_symbol(node):
    return SymbolType(node.name), set()


def infer_literal(node):
    if node.value.replace('.', '').isdigit():
        if '.' in node.value:
            return Types.Double, set()
        return Types.Integer, set()

    return Types.String, set()


def infer_binary_operator(node):
    type_a, _ = infer(node.first)
    type_b, _ = infer(node.second)

    if type_a == type_b:
        return type_a, set()

    return type_a, set([(type_a, type_b)])

def infer_invocation(node):
    return SymbolType(node.func.name), set()

def infer_return(node):
    return infer(node.result)

def infer_assignment(node):
    return infer(node.src)

def infer_block(node):
    types = set()
    constrains = set()

    for statement in node.body:
        if type(statement) in (Return, IfStatement):
            t, cs = infer(statement)
            types.add(t)

        for c in cs:
            constrains.add(c)

    if len(types) > 1:
        constrains.add(tuple(types))

    return types.pop(), constrains

def infer_function(node):
    return infer(node.body)


def infer_if_statement(node):
    _, cs = infer(node.expression)
    constrains = set(cs)
    t, cs = infer(node.body)
    constrains = constrains.union(cs)

    return t, constrains

def is_concrete_type(typ):
    return isinstance(typ, Types)

def resolve_types(constrains):
    out = {}
    for constrain in constrains:
        types = set(filter(is_concrete_type, constrain))
        if len(types) > 1:
            raise InferenceError('cannot solve constrain %s' % ','.join(map(str, constrain)))

        t = types.pop()
        for symbol in set(filterfalse(is_concrete_type, constrain)):
            out[symbol] = t

    return out


def infer(node, known={}):
    infers = {
        Function: infer_function,
        Return: infer_return,
        Literal: infer_literal,
        Symbol: infer_symbol,
        Invocation: infer_invocation,
        Assignment: infer_assignment,
        BinaryOperator: infer_binary_operator,
        Block: infer_block,
        IfStatement: infer_if_statement
        }

    default = lambda node: None
    return infers.get(type(node), default)(node)
