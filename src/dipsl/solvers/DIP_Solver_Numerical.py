import numpy as np
from pydantic import BaseModel

from .DIP_Solver_Units import UnitSolver
from ..nodes.DIP_Parser import Parser
from ..DIP_Environment import Environment
from ..DIP_Unit import Unit

class NumericalSolver(BaseModel):

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

    def equal(self, expr1, expr2):
        unit1 = self.solve(expr1)
        unit2 = self.solve(expr2)
        if unit1 == unit2:
            return True
        else:
            print('left:', expr1, unit1.num, unit1.base)
            print('right:',expr2, unit2.num, unit2.base)
            return False

    def _parse_unary(self, expr):
        p, sign, expr = 1, expr[1], expr[2:]
        left = ''
        while p>0 and expr:
            if sign=='(': p += 1
            elif sign==')':
                if  p==1: break
                else: p -= 1
            left = left + sign
            sign, expr = expr[0], expr[1:]
        return self.solve(left), expr

    def _parse_binary(self, expr):
        p, sign, expr = 1, expr[1], expr[2:]
        left = ''
        while p>0 and expr:
            if sign=='(': p += 1
            elif sign==')':
                if  p==1: break
                else: p -= 1
            left = left + sign
            sign, expr = expr[0], expr[1:]
        left1, left2 = left.split(',')
        return self.solve(left1), self.solve(left2), expr    
    
    def _parse_atom(self, expr):
        expr = expr.lstrip()
        # unary operations
        fns = {
            'exp':np.exp,'ln':np.log,'log10':np.log10,
            'sin':np.sin,'cos':np.cos
        }
        for name, fx in fns.items():
            if expr[:len(name)+1]==name+'(':
                left, expr = self._parse_unary(expr[len(name):])
                if not left.isnumeric():
                    raise Exception(f"Operation '{name}' only dimensionless values", expr)
                value = fx(left.number())
                return Unit(value), expr
        # binary operations
        if expr[:4]=='pow(':
            left1, left2, expr = self._parse_binary(expr[3:])
            if not left2.isnumeric():
                raise Exception("Power exponent accepts only dimensionless values", expr)
            value = left1 ** left2.number()
            return value, expr
        # atom is in parentheses
        elif expr[0]=='(':
            return self._parse_unary(expr)
        # atom is a numerical value
        else:
            kwargs = {'code': expr, 'line':0, 'source': 'expression'}
            p = Parser(keyword='node',**kwargs)
            p.part_value()
            if p.value_ref:   # import existing node
                nodes = self.env.request(p.value_ref, count=[0,1])
                if len(nodes)==1:
                    node = nodes[0]
                    value, units = node.value.value, node.value.unit
                else:
                    raise Exception('Reference does not return any nodes:', p.value_ref)
            else:             # create anonymous node
                p.part_units()
                value, units = p.value_raw, p.units_raw
            with UnitSolver(self.env) as s:
                if units:
                    unit = s.solve(units) * s.unit(value)
                else:
                    unit = s.unit(value)
            unit.symbol = expr
            return unit, p.ccode

    def _parse_sign(self, expr):
        expr = expr.lstrip()
        return expr[0], expr[1:]

    def _solve(self, expr):
        left, expr = self._parse_atom(expr)
        if expr:
            while expr:
                sign, expr = self._parse_sign(expr)
                if sign=='*':
                    right, expr = self._parse_atom(expr)
                    with UnitSolver(self.env) as s:
                        left = left * right
                elif sign=='/':
                    right, expr = self._parse_atom(expr)
                    with UnitSolver(self.env) as s:
                        left = left / right
                else:
                    return left, sign + expr
        return left, expr                    
    
    def solve(self, expr, in_units=None):
        expr_bak = expr
        # immediately return boolean values
        if isinstance(expr,(int,float)):
            return expr
        # check if parenthesis are properly terminated
        elif expr.count('(')!=expr.count(')'):
            raise Exception('Unterminated parenthesis in expression:', expr)
        expr = expr.strip()
        # evaluate parenthesis and basic operations
        left, expr = self._solve(expr)
        if expr:
            while expr:
                sign, expr = self._parse_sign(expr)
                if sign=='+':
                    right, expr = self._solve(expr)
                    left = left + right
                elif sign=='-':
                    right, expr = self._solve(expr)
                    left = left - right
        if in_units:
            with UnitSolver(self.env) as s:
                iunit = s.solve(in_units)
                if not left.eqdim(iunit):
                    raise Exception("Expression result dimensions do not match node dimensions:",expr_bak,in_units)
                unit = left / iunit
            return unit.number()
        else:
            return left

