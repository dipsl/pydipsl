from pydantic import BaseModel
from typing import List
import numpy as np
from math import isclose

from .DIP_UnitList import *
from .settings import Numeric

class Unit(BaseModel):
    num: float         # number value
    base: List[int]    # unit dimension exponents
    dfn: str = None    # definition expression
    symbol: str = None # symbol
    symbol_base: str = None  # symbol without prefix
    name: str = None   # full name
    arbitrary: bool = False  # is unit arbitrary?

    def __init__(self, num, base=None, **kwargs):
        kwargs['num'] = num
        if base:
            kwargs['base'] = base
        else:
            kwargs['base'] = [0]*len(UnitList_Base)
        super().__init__(**kwargs)
        self._rebase()
        
    def __add__(self, other):
        if not self.eqdim(other):
            raise Exception(
                'Addition of two units with different dimensions is not allowed',
                self.symbol,
                other.symbol
            )
        num = self.number() + other.number()
        base = [0] + self.dimension()
        return Unit(num, base)

    def __sub__(self, other):
        if not self.eqdim(other):
            raise Exception(
                'Substraction of two units with different dimensions is not allowed',
                self.symbol,
                other.symbol
            )
        num = self.number() - other.number()
        base = [0] + self.dimension()
        return Unit(num, base)
    
    def __mul__(self, other):
        num = self.num*other.num
        base = [self.base[i]+other.base[i] for i in range(len(self.base))]
        return Unit(num, base)

    def __truediv__(self, other):
        num = self.num/other.num
        base = [self.base[i]-other.base[i] for i in range(len(self.base))]
        return Unit(num, base)

    def __pow__(self, power):
        num = self.num**power
        base = [self.base[i]*power for i in range(len(self.base))]
        return Unit(num, base)

    def __eq__(self, other):
        if not isclose(self.num, other.num, rel_tol=Numeric.PRECISION):
            return False
        if self.base!=other.base:
            return False
        return True
    
    def _rebase(self):
        if self.num<0:
            exp = int(np.floor(np.log10(-self.num)))
            num = self.num/10**exp
        elif self.num==0:
            exp = 0
            num = 0
        else:
            exp = int(np.floor(np.log10(self.num)))
            num = self.num/10**exp
        self.num = num
        self.base[0] += exp

    def isnumeric(self):
        return np.all([d==0 for d in self.dimension()])
    
    def eqnum(self, other):
        return self.base[0]==other.base[0] and \
            isclose(self.num, other.num, rel_tol=Numeric.PRECISION)
    
    def eqdim(self, other):
        return self.dimension()==other.dimension()

    def copy(self):
        return Unit(
            self.num, self.base,
            dfn = self.dfn,
            symbol = self.symbol,
            symbol_base = self.symbol_base,
            name = self.name,
            arbitrary = self.arbitrary
        )
    
    def number(self):
        return self.num * 10**self.base[0]

    def dimension(self):
        return self.base[1:]

    def inunitsof(self, other):
        if not self.eqdim(other):
            raise Exception(f"Units '{self.symbol}' and '{other.symbol}' cannot be converted")
        if self.arbitrary or other.arbitrary:
            return Convert_Arbitrary(self, other)
        else:
            return self / other
