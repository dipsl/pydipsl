import numpy as np
from math import isclose
from pydantic import BaseModel

from ..DIP_Environment import Environment
from ..nodes.DIP_Parser import Parser
from ..datatypes import NumberType, BooleanType, FloatType, IntegerType, StringType
from ..DIP_Settings import *

class LogicalSolver(BaseModel):

    env: Environment
    
    def __init__(self, env:Environment=None, **kwargs):
        if env:
            kwargs['env'] = env
        else:
            kwargs['env'] = Environment()
        super().__init__(**kwargs)
            
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass
    
    def _eval_node(self, expr):
        expr = expr.strip()
        if expr=='':
            return None
        flags = []
        if expr[0]==SGN_NEGATE:
            flags.append('negate')
            expr = expr[1:]
        if expr[0]==SGN_DEFINED:
            flags.append('defined')
            expr = expr[1:]
        # parse node from the code
        kwargs = {'code': expr, 'line':0, 'source': 'expression'}
        p = Parser(keyword='node',**kwargs)
        p.part_value()
        if p.value_ref:   # import existing node
            nodes = self.env.request(p.value_ref, count=[0,1])
            if len(nodes)==1:
                if 'defined' in flags:
                    node = BooleanType(True)
                else:
                    node = nodes[0].value
            elif len(nodes)==0:
                if 'defined' in flags:
                    node = BooleanType(False)
                else:
                    node = None
        elif p.value_raw==KWD_TRUE:
            node = BooleanType(True)
        elif p.value_raw==KWD_FALSE:
            node = BooleanType(False)
        else:            # create anonymous node
            p.part_units()
            node = NumberType(p.value_raw, p.units_raw)
        if 'negate' in flags:
            if isinstance(node, BooleanType):
                node.value = False if node.value else True
            else:
                raise Exception(f"Negated node is not boolean but:", node.keyword)
        return node

    def _solve_comparison(self, expr):
        # return immediatelly if expression is a boolean
        if isinstance(expr,(BooleanType,np.bool_)):
           return expr
        expr = expr.strip()
        # list of comparison opperators
        def _equal_operation(a,b):
            if isinstance(a,str) and isinstance(b,str):
                return a==b
            else:
                return isclose(a, b, rel_tol=EQUAL_PRECISION)            
        comps = [
            # neglect python rounding errors using 'isclose' function
            ('==', _equal_operation),  
            ('!=', lambda a,b: a!=b),
            ('>=', lambda a,b: (a>b)|isclose(a, b, rel_tol=EQUAL_PRECISION)),
            ('<=', lambda a,b: (a<b)|isclose(a, b, rel_tol=EQUAL_PRECISION)),
            ('>',  lambda a,b: a>b ),
            ('<',  lambda a,b: a<b ),
        ]
        # evaluate pair comparisions
        for sign,fn in comps:
            if sign not in expr:
                continue
            # parse left and right nodes
            left,right = expr.split(sign)
            left,right = self._eval_node(left),self._eval_node(right)
            if not left or not right:
                raise Exception("Couldn't find all requested nodes:", expr)
            # perform comparison
            if not isinstance(left, (IntegerType,FloatType,StringType,BooleanType)):
                # if left node datatype is unknown
                if isinstance(right, (IntegerType,FloatType)):
                    left.convert(right.unit, self.env)
                return fn(right.dtype(left.value), right.value)
            elif not isinstance(right, (IntegerType,FloatType,StringType,BooleanType)):
                # if right node datatype is unknown
                if isinstance(left, (IntegerType,FloatType)):
                    right.convert(left.unit, self.env)
                return fn(left.value, left.dtype(right.value))
            elif type(left)==type(right):
                # if both datatypes are known
                if isinstance(left, (IntegerType,FloatType)):
                    left.convert(right.unit, self.env)
                return fn(left.value, right.value)                
            else:                               # throw error if both datatypes are unknown
                raise Exception("Invalid comparison:", expr)
        # evaluate single comparisons
        node = self._eval_node(expr)
        if isinstance(node, BooleanType):
            return node.value
        else:
            raise Exception("Single node expression needs to be a boolean:", expr)

    def solve(self, expr):
        # immediately return boolean values
        if isinstance(expr,(bool,np.bool_)):
            return expr
        # check if parenthesis are properly terminated
        elif expr.count('(')!=expr.count(')'):
            raise Exception('Unterminated parenthesis in expression:', expr)
        expr = expr.strip()
        # evaluate logical && and || and parenthesis
        ors, ands, buff = [], [], ''
        while expr:
            sign, expr = expr[0], expr[1:]
            if sign=='(': # evaluate content of parenthesis separately
                p = 1
                while p>0 and expr:
                    sign, expr = expr[0], expr[1:]
                    if sign=='(':   p += 1
                    elif sign==')' and p==1: break
                    elif sign==')' and p>1: p -= 1
                    buff = buff + sign
                buff = self.solve(buff)        # evaluate in subroutine
                expr = expr.lstrip()
            elif expr and sign+expr[0]=='||':  # evaluate logical 'or' with priority
                expr = expr[1:]                # skip the second pipe
                if ands:                       # terminate openned 'and' clause
                    ands.append(buff)
                    buff = np.all([self._solve_comparison(a) for a in ands])
                    ands = []
                ors.append(buff)
                buff = ''
            elif expr and sign+expr[0]=='&&':  # evaluate logical 'and'
                expr = expr[1:]                # skip the second ampersend
                ands.append(buff)
                buff = ''
            elif sign in ['\n','\t']:          # remove special characters
                continue
            else:
                buff = buff + sign             # add character to a buffer
        if ands:                               # terminate last openned 'and' clause
            ands.append(buff)
            buff = np.all([self._solve_comparison(a) for a in ands])
        ors.append(buff)                       # terminate 'or' clause
        return np.any([self._solve_comparison(o) for o in ors])    

