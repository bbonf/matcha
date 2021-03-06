from nose.tools import eq_, assert_is_instance

from matcha.ast import (Invocation, Function, Assignment,
    BinaryOperator, IfStatement, Return, Block, NumericLiteral,
    StringLiteral, Symbol, ListLiteral)
from matcha.parsing.base import joined, match
from matcha.parsing import (symbol, atom, invocation, function,
    oneof, arguments, assignment, binary_operator,
    if_statement, return_statement, literal)

def full_match(parser, string, node=None):
    if node:
        eq_(parser(string), (node, ''))
    else:
        eq_(parser(string), (string, ''))

def no_match(parser, string):
    eq_(parser(string), None)

class TestJoined():
    def test_matches(self):
        p = joined(match(','), match('a'))
        eq_(p('a,a'), (['a', ',', 'a'], ''))
        eq_(p('a.a'), (['a'], '.a'))
        eq_(p('a,a,'), (['a', ',', 'a'], ''))

class TestOneof():
    def test_oneof(self):
        p = oneof(['a','b','+','foo'])
        full_match(p, 'a')
        full_match(p, 'b')
        full_match(p, '+')
        full_match(p, 'foo')

        no_match(p, 'something')
        no_match(p, 'else a')

class TestSymbol():
    def test_matches(self):
        p = symbol()
        full_match(p, 'simple')
        full_match(p, 'snake_case')
        full_match(p, 'lowerAndUpper')
        full_match(p, 'end_with_digit1')

        eq_(p('with_whitespace '), ('with_whitespace', ''))

    def test_fails(self):
        p = symbol()
        no_match(p, '1start_with_digit')
        no_match(p, '1hello')
        eq_(p('with space'), ('with', 'space'))

class TestAtom():
    def test_matches(self):
        p = atom()
        full_match(p, 'symbol', Symbol('symbol'))
        full_match(p, '"double_quote"', StringLiteral('"double_quote"'))
        full_match(p, "'single_quote'", StringLiteral("'single_quote'"))
        full_match(p, '1234', NumericLiteral('1234'))
        full_match(p, 'dotted.name', Symbol('dotted.name'))

        full_match(p, 'a', Symbol('a'))

    def test_fails(self):
        p = atom()
        no_match(p, '{}weird')
        no_match(p, '')
        eq_(p('more than one'), (Symbol('more'), 'than one'))

class TestInvocation():
    def test_simple(self):
        p = invocation()
        node, r = p('module.func(symbol, 123,"string")')

        eq_(r, '')
        assert_is_instance(node, Invocation)
        eq_(node.func, Symbol('module.func'))
        eq_(node.args[0], Symbol('symbol'))
        eq_(node.args[1], NumericLiteral('123'))
        eq_(node.args[2], StringLiteral('"string"'))

    def test_no_arguments(self):
        p = invocation()
        node, r = p('module.func()')

        eq_(r, '')
        assert_is_instance(node, Invocation)
        eq_(node.func, Symbol('module.func'))
        eq_(node.args, [])


def test_assignment():
    p = assignment()
    five = NumericLiteral('5')
    x = Symbol('x')
    eq_(p('x=5')[0], Assignment(five, x))
    eq_(p('x =5')[0], Assignment(five, x))
    eq_(p('x= 5')[0], Assignment(five, x))
    eq_(p('x = 5')[0], Assignment(five, x))

def test_arguments():
    p = arguments()
    eq_(p('(a,b,c)')[0], ['a','b','c'])
    eq_(p('(a, b, c)')[0], ['a','b','c'])

def test_binary():
    p = binary_operator()
    node, r = p('a + b')

    eq_(r, '')
    assert_is_instance(node, BinaryOperator)
    eq_(node.first, Symbol('a'))
    eq_(node.operator, '+')
    eq_(node.second, Symbol('b'))

    node, r = p('a + b + c')

    eq_(r, '')
    assert_is_instance(node, BinaryOperator)
    eq_(node.first, Symbol('a'))
    eq_(node.operator, '+')
    eq_(node.second, BinaryOperator(
        Symbol('b'), '+', Symbol('c')))

    node, r = p('a + b + c + d')

    eq_(r, '')
    assert_is_instance(node, BinaryOperator)
    eq_(node.first, Symbol('a'))
    eq_(node.operator, '+')
    eq_(node.second,
            BinaryOperator(Symbol('b'), '+',
                BinaryOperator(
                    Symbol('c'),
                    '+',
                    Symbol('d'))))

class TestFunction():
    def test_simple(self):
        p = function(0)
        node, r = p(
            'def test_func(arg1, arg2):\n'
            '    x = 5')

        eq_(r, '')
        assert_is_instance(node, Function)
        eq_(node.name, 'test_func')
        eq_(node.args[0], 'arg1')
        eq_(node.args[1], 'arg2')
        eq_(node.body.body, [
            Assignment(NumericLiteral('5'), Symbol('x'))])

    def test_missing_body(self):
        p = function(0)
        eq_(p(
            'def test_func(arg1, arg2):\n(!)@#!('),
            None)

    def test_no_arguments(self):
        p = function(0)
        node, r = p(
            'def just_five():\n'
            '    return 5')

        eq_(node.name, 'just_five')
        eq_(node.args, [])
        eq_(node.body.body, [
            Return(NumericLiteral('5'))])



class TestIfStatement():
    def test_simple(self):
        p = if_statement()
        node, r = p(
            'if x > 5:\n'
            '    x = 8')

        eq_(r, '')
        assert_is_instance(node, IfStatement)
        eq_(node.expression,
            BinaryOperator(Symbol('x'), '>', NumericLiteral('5')))
        eq_(node.body.body, [
            Assignment(NumericLiteral('8'), Symbol('x'))])

    def test_nested(self):
        p = if_statement()
        node, r = p(
            'if x > 5:\n'
            '    x = 8\n'
            '    if y == 3:\n'
            '        y = 0\n')


        eq_(r, '')
        assert_is_instance(node, IfStatement)
        eq_(node.expression,
            BinaryOperator(Symbol('x'), '>', NumericLiteral('5')))
        eq_(node.body.body, [
            Assignment(NumericLiteral('8'), Symbol('x')),
            IfStatement(
                BinaryOperator(Symbol('y'), '==', NumericLiteral('3')),
                Block([Assignment(NumericLiteral('0'), Symbol('y'))])
            )])


def test_retrun():
    p = return_statement()
    node, r = p('return 5')

    eq_(r, '')
    assert_is_instance(node, Return)
    eq_(node.result, NumericLiteral('5'))

def test_list_literal():
    p = literal()

    full_match(p, '[1,2,3]', ListLiteral(
        [NumericLiteral(x) for x in ['1','2','3']]))

