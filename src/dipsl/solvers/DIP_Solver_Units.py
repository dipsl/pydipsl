import numpy as np
import re
from math import isclose
from pydantic import BaseModel

from ..DIP_Unit import Unit
from ..DIP_Environment import Environment
from ..DIP_UnitList import *
from ..DIP_Settings import *

class UnitSolver(BaseModel):

    base: dict
    nbase: int
    npbase: int
    prefixes: dict 
    derivates: dict
    arbitrary: dict
    units: dict
    custom: dict = None
    
    def __init__(self, env:Environment=None, **kwargs): 
        kwargs['nbase'] = len(UnitList_Base)
        kwargs['npbase'] = kwargs['nbase']-1
        # Load unit lists into dictionaries
        kwargs['base'] = {}
        for unit in UnitList_Base:
            kwargs['base'][unit[2]] = Unit(
                unit[0], unit[1], symbol=unit[2], name=unit[3]
            )
        kwargs['prefixes'] = {}
        for unit in UnitList_Prefixes:
            kwargs['prefixes'][unit[2]] = Unit(
                unit[0], unit[1], symbol=unit[2], dfn=unit[3], name=unit[4]
            )
        kwargs['derivates'] = {}
        for unit in UnitList_Derivates:
            kwargs['derivates'][unit[2]] = Unit(
                unit[0], unit[1], symbol=unit[2], dfn=unit[3], name=unit[4]
            )
        kwargs['arbitrary'] = {}
        for unit in UnitList_Arbitrary:
            kwargs['arbitrary'][unit[1]] = Unit(
                1.0, unit[0], symbol=unit[1], name=unit[2], arbitrary=True
            )
        kwargs['units'] = kwargs['base'] | kwargs['derivates'] | kwargs['arbitrary']
        if env and env.units:
            kwargs['custom'] = {}
            for unit in env.units.values():
                if unit.symbol in kwargs['units']:
                    raise Exception('Following unit already exists:', unit.symbol)
                kwargs['custom'][unit.symbol] = unit
            kwargs['units'] = kwargs['units'] | kwargs['custom']
        super().__init__(**kwargs)
            
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass
    
    def unit(self, string=None):
        # parse number
        m = re.match(r'^[-]?([0-9.]+)(e([0-9+-]+)|)$', str(string))
        if m:
            num = float(string)
            return Unit(num)
        # parse unit
        string_bak = string
        exp, base, prefix = '', '', ''
        symbol, string = string[-1], ' '+string[:-1]
        # parse exponent
        while len(string):
            if not re.match('^[0-9+-]{1}$', symbol):
                break
            exp = symbol+exp
            symbol, string = string[-1], string[:-1]
        # parse unit symbol
        unitkeys = self.units.keys()
        while len(string):
            nbase = len(base)+1
            ukeys = [key[-nbase:] for key in unitkeys]
            if symbol+base not in ukeys:
                break
            base = symbol+base
            symbol, string = string[-1], string[:-1]
        # parse unit prefix
        while len(string):
            prefix = symbol+prefix
            symbol, string = string[-1], string[:-1]
            if symbol==' ':
                break
        # apply prefix
        if prefix:
            if prefix not in self.prefixes.keys():
                raise Exception(f"Unit prefix '{prefix}' is not available in: {string_bak}")
            unit = self.prefixes[prefix] * self.units[base]
        else:
            unit = self.units[base].copy()
        # apply exponent
        if exp:
            unit = unit**int(exp)
        unit.arbitrary = self.units[base].arbitrary
        unit.symbol_base = base
        #print("%-06s"%string_bak, "%-03s"%prefix, "%-03s"%base, "%03s"%exp, unit.num)
        return unit

    def solve(self, right, expr_bak=None):
        if not expr_bak:
            expr_bak = right
        if right.count('(')!=right.count(')'):
            raise Exception(f"Unmatched parentheses in: {expr_bak}")
        left = ''
        symbol, right = right[0], right[1:]
        parentheses = 0
        while right:
            if symbol=='*':
                return self.solve(left, expr_bak) * self.solve(right, expr_bak)
            elif symbol=='/':
                if '/' in right:
                    # If there are multiple divisions
                    # we need to start from the last
                    parts = right.split('/')
                    right = parts.pop()
                    parts.insert(0,left)
                    left = '/'.join(parts)
                return self.solve(left, expr_bak) / self.solve(right, expr_bak)
            elif symbol=='(':
                parentheses = 1
                symbol, right = right[0], right[1:]
                while parentheses>0:
                    if symbol=='(':
                        parentheses+=1
                    elif symbol==')':
                        parentheses-=1
                    else:
                        left = left + symbol
                    if not right:
                        return self.solve(left)
                    symbol, right = right[0], right[1:]
            else:
                left = left + symbol
                symbol, right = right[0], right[1:]
        unit = self.unit(left+symbol)
        unit.symbol = expr_bak
        return unit
