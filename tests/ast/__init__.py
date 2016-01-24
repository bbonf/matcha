from nose.tools import eq_, raises

from matcha.ast import Literal, Return, BinaryOperator, Symbol
from matcha.ast.inference import (Types, infer_literal, infer_return,
    infer_function, infer_binary_operator, InferenceError, SymbolType, resolve_types)
from matcha.parsing import function


def test_infer_literal():
    integer = Literal('2')
    double = Literal('2.4')
    string = Literal('hello')

    eq_(infer_literal(integer), (Types.Integer, set()))
    eq_(infer_literal(double), (Types.Double, set()))
    eq_(infer_literal(string), (Types.String, set()))


def test_infer_return():
    ret = Return(Literal('2'))

    eq_(infer_return(ret), (Types.Integer, set()))


def test_infer_binary():
    binary = BinaryOperator(Literal('2'), '+', Literal('5'))

    eq_(infer_binary_operator(binary), (Types.Integer, set()))


    binary = BinaryOperator(Literal('2'), '+', Symbol('hello'))

    eq_(infer_binary_operator(binary),
        (Types.Integer, {(Types.Integer, SymbolType('hello'))}))


def test_infer_function():
    func, _ = function(0)(
        'def just_two(x):\n'
        '    if x > 5:\n'
        '        return 3\n'
        '    return 2')

    eq_(infer_function(func), (Types.Integer, {(SymbolType('x'), Types.Integer)}))


def test_infer_error():
    func, _ = function(0)(
        'def just_two(x):\n'
        '    if x > 5:\n'
        '        return "hello"\n'
        '    return 2')

    #eq_(infer_function(func)[1], {(Types.Integer, Types.String),})

def test_resolve_types():
    constrains = set([
        (SymbolType('x'), Types.Integer),
        (Types.String, SymbolType('y'), SymbolType('z')),
        ])

    solution = resolve_types(constrains)
    eq_(solution[SymbolType('x')], Types.Integer)
    eq_(solution[SymbolType('y')], Types.String)
    eq_(solution[SymbolType('z')], Types.String)

@raises(InferenceError)
def test_resolve_types_fail():
    constrains = set([
        (Types.String, Types.Integer),
        ])

    eq_(resolve_types(constrains), None)

def test_infer_argument():
    func, _ = function(0)(
        'def double(x):\n'
        '    return x * 2')

    ret, constrains = infer_function(func)
    eq_(ret, SymbolType('x'))
    eq_(constrains, {(SymbolType('x'), Types.Integer)})

