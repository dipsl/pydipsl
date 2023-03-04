from .DIP_Node import Node
from ..DIP_Settings import *
from ..solvers import LogicalSolver

class CaseNode(Node):
    keyword: str = 'case'

    @staticmethod
    def is_node(parser):
        parser.kwd_case()
        if parser.is_parsed('kwd_case'):
            if parser.name.endswith(SGN_CONDITION + KWD_CASE):
                parser.part_value()
            parser.part_comment()
            return CaseNode(parser)
            
    def parse(self, env):
        # Solve case
        if self.name.endswith(SGN_CONDITION + KWD_CASE):
            with LogicalSolver(env) as s:
                if self.value_expr:
                    self.value = s.solve(self.value_expr)
                else:
                    self.value = s.solve(self.value_raw)
        return None
