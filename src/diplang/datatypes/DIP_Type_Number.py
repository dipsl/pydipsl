import numpy as np

from .DIP_Type import Type
from ..DIP_Unit import Unit
import diplang

class NumberType(Type):
    
    def convert(self, unit, env=None):
        """ Convert units of this type
        """
        if self.unit and unit and self.unit!=unit:
            with diplang.solvers.UnitSolver(env) as s:
                unit1 = s.solve(self.unit)
                unit11 = unit1 * Unit(self.value)
                unit11.symbol_base = unit1.symbol_base
                unit11.arbitrary = unit1.arbitrary        
                unit2 = s.solve(unit)
                unit3 = unit11.inunitsof(unit2)
                self.value = unit3.number()
                self.unit = unit
