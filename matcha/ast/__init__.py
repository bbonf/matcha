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
Import = namedtuple('Import', 'name')

NumericLiteral = namedtuple('NumericLiteral', 'value')
StringLiteral = namedtuple('StringLiteral', 'value')
ListLiteral = namedtuple('ListLiteral', 'value')


def get_imports(ast):
    return map(
        lambda node: node.name,
        filter(lambda node: type(node) == Import, ast))
