from typing import List
from pydantic import BaseModel

from .DIP_Node import Node
from ..solvers import TemplateSolver
from ..datatypes import StringType

class StringNode(Node):
    keyword: str = 'str'
    options: List[BaseModel] = []
    format: str = None

    @staticmethod
    def is_node(parser):
        if parser.keyword=='str':
             parser.part_dimension()
             parser.part_equal()
             if parser.is_parsed('part_equal'): # definition
                 parser.part_value()  
             else:
                 parser.defined = True  # declaration
             parser.part_units()    
             parser.part_comment()
             return StringNode(parser)
         
    def set_value(self, value=None):
        """ Set value using value_raw or arbitrary value
        """
        if value is None and self.value_raw:
            self.value = StringType(self.cast_value())
        elif value:
            self.value = StringType(value)
        else:
            self.value = None
            
    def parse(self, env):
        if self.value_expr: # Process function
            with TemplateSolver(env) as s:
                self.value_raw = s.solve(self.value_expr)
        if self.units_raw:
            raise Exception('String datatype does not support units:', self.code)
        return None    
