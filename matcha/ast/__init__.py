from enum import Enum
from collections import namedtuple

Node = Enum('Node', 'function')
Function = namedtuple('Function', 'name,args,body')
Invocation = namedtuple('Invocation', 'func,args')
Assignment = namedtuple('Assignment', 'src,dst')

def Statement(**args):
    print(args)
