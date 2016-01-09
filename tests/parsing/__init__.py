from nose.tools import eq_, assert_is_instance

from matcha.ast import Invocation, Function, Assignment
from matcha.parsing.base import joined, match
from matcha.parsing import (symbol, atom, invocation, function,
    oneof, arguments, assignment)

def full_match(parser, string):
    eq_(parser(string), (string, ''))

def no_match(parser, string):
    eq_(parser(string), None)

class TestJoined():
    def test_matches(self):
        p = joined(match(','), match('a'))
        eq_(p('a,a'), (['a', ',', 'a'], ''))
        eq_(p('a.a'), (['a'], '.a'))

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
        full_match(p, 'symbol')
        full_match(p, '"double_quote"')
        full_match(p, "'single_quote'")
        full_match(p, "1234")
        full_match(p, 'dotted.name')

        full_match(p, 'a')

    def test_fails(self):
        p = atom()
        no_match(p, '{}weird')
        no_match(p, '')
        eq_(p('more than one'), ('more', 'than one'))

class TestInvocation():
    def test_simple(self):
        p = invocation()
        node, r = p('module.func(symbol, 123,"string")')

        eq_(r, '')
        assert_is_instance(node, Invocation)
        eq_(node.func, 'module.func')
        eq_(node.args[0], 'symbol')
        eq_(node.args[1], '123')
        eq_(node.args[2], '"string"')


def test_assignment():
    p = assignment()
    eq_(p('x=5')[0], Assignment(src='5', dst='x'))
    eq_(p('x =5')[0], Assignment(src='5', dst='x'))
    eq_(p('x= 5')[0], Assignment(src='5', dst='x'))
    eq_(p('x = 5')[0], Assignment(src='5', dst='x'))

def test_arguments():
    p = arguments()
    eq_(p('(a,b,c)')[0], ['a','b','c'])
    eq_(p('(a, b, c)')[0], ['a','b','c'])

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
        eq_(node.body, [Assignment(src='5', dst='x')])

    def test_missing_body(self):
        p = function(0)
        eq_(p(
            'def test_func(arg1, arg2):\n(!)@#!('),
            None)



