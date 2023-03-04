from .DIP_Node import Node
from ..DIP_Environment import Environment
from ..DIP_Settings import *

class ImportNode(Node):
    keyword: str = 'import'

    def is_node(parser):
        parser.part_reference()
        if parser.is_parsed('part_reference'):
            parser.part_comment()
            return ImportNode(parser)
    
    def inject_value(self, env:Environment, node=None):
        pass
    
    def parse(self, env):
        # Parse import code
        nodes_new = []
        for node in env.request(self.value_ref):
            path = self.name.split(SGN_SEPARATOR + '{')
            path.pop()
            path.append(node.name)                
            node.source = self.source
            node.line = self.line
            node.name = SGN_SEPARATOR.join(path)
            node.indent = self.indent
            nodes_new.append(node)
        return nodes_new
