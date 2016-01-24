from collections import namedtuple

Function = namedtuple('Function', 'name,args,body')
Invocation = namedtuple('Invocation', 'func,args')
Assignment = namedtuple('Assignment', 'src,dst')
BinaryOperator = namedtuple(
    'BinaryOperator', 'first,operator,second')
IfStatement = namedtuple('IfStatement', 'expression,body')
Block = namedtuple('Block', 'body')
Return = namedtuple('Return', 'result')
Symbol = namedtuple('Symbol', 'name')

Literal = namedtuple('Literal', 'value')
ListLiteral = namedtuple('ListLiteral', 'value')
