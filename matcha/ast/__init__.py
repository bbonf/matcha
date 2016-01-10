from enum import Enum
from collections import namedtuple

Node = Enum('Node', 'function')
Function = namedtuple('Function', 'name,args,body')
Invocation = namedtuple('Invocation', 'func,args')
Assignment = namedtuple('Assignment', 'src,dst')
BinaryOperator = namedtuple(
    'BinaryOperator', 'first,operator,second')
IfStatement = namedtuple('IfStatement', 'expression,body')
Block = namedtuple('Block', 'body')
Return = namedtuple('Return', 'result')
Literal = namedtuple('Literal', 'value')
Symbol = namedtuple('Symbol', 'name')


def Statement(**args):
    print(args)
