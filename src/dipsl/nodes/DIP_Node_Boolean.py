from .DIP_Node import Node
from ..solvers import LogicalSolver
from ..datatypes import BooleanType

class BooleanNode(Node):
    keyword: str = 'bool'
    value: bool = None
    dtype = bool

    @staticmethod
    def is_node(parser):
        if parser.keyword=='bool':
             parser.part_dimension()
             parser.part_equal()
             if parser.is_parsed('part_equal'): # definition
                 parser.part_value()  
             else:
                 parser.defined = True  # declaration
             parser.part_units()    
             parser.part_comment()
             return BooleanNode(parser)
    
    def set_value(self, value=None):
        """ Set value using value_raw or arbitrary value
        """
        if value is None:  # == None
            if self.value_raw:
                self.value = BooleanType(self.cast_value())
            else:
                self.value = None
        else:              # == True/False
            self.value = BooleanType(value)
            
    def parse(self, env):
        if self.value_expr: # Process function
            with LogicalSolver(env) as s:
                self.value_raw = s.solve(self.value_expr)
        if self.units_raw:
            raise Exception('Boolean datatype does not support units:', self.code)
        return None    
