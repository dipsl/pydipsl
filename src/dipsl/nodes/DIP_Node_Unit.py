from . import Node
from . import Parser
from ..settings import Namespace
from ..solvers import UnitSolver

class UnitNode(Node):
    keyword: str = 'unit'

    @staticmethod
    def is_node(parser):
        parser.kwd_unit()
        if parser.is_parsed('kwd_unit'):
            parser.part_comment()
            return UnitNode(parser)
    
    def parse(self, env):
        parser = Parser(
            code=self.value_raw,
            line=self.line,
            source=self.source
        )
        # import a remote source
        parser.part_reference()
        if parser.is_parsed('part_reference'):
            units = env.request(parser.value_ref, namespace=Namespace.UNITS)
            for key,val in units.items():
                env.add_unit(key, val)
        else:
            # inject value of a node
            parser.part_name(path=False) # parse name
            parser.part_equal()          # parse equal sign
            parser.part_value()          # parse value
            if parser.value_ref:
                self.inject_value(env, parser)
            parser.part_units()          # parse unit
            with UnitSolver(env) as s:
                unit = s.solve(parser.units_raw) * s.unit(parser.value_raw)
                unit.symbol = '['+parser.name+']'
                env.add_unit(parser.name, unit)
        return None
