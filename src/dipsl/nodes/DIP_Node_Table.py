import csv

from .DIP_Node import Node
from .DIP_Parser import Parser
from . import BooleanNode, IntegerNode, FloatNode, StringNode
from ..settings import Sign

class TableNode(Node):
    keyword: str = 'table'
    
    @staticmethod
    def is_node(parser):
        if parser.keyword=='table':
             parser.part_dimension()
             parser.part_equal()
             if parser.is_parsed('part_equal'): # definition
                 parser.part_value()  
             else:
                 parser.defined = True  # declaration
             parser.part_units()    
             parser.part_comment()
             return TableNode(parser)
         
    def parse(self, env):
        lines = self.value_raw.split("\n")
        # Parse nodes from table header
        table = []
        while len(lines)>0:
            line = lines.pop(0)
            if line.strip()=='':
                break
            # Parse node parameters
            parser = Parser(
                code=line,
                line=self.line,
                source=self.source
            )
            parser.part_name()      # parse node name
            parser.part_type()      # parse node type
            parser.part_units()     # parse node units
            if not parser.is_empty():
                raise Exception(f"Incorrect header format: {line}")
            # Initialize actual node
            types = {
                'bool':  BooleanNode,
                'int':   IntegerNode,
                'float': FloatNode,
                'str':   StringNode,
            }
            if parser.keyword in types:
                node = types[parser.keyword](parser)
                node.value_raw = []
                table.append(node)
            else:
                raise Exception(f"Incorrect format or missing empty line after header: {self.code}")
        # Remove whitespaces from all table rows
        for l,line in enumerate(lines):
            lines[l] = line.strip()
            if line=='': del lines[l]
        # Read table and assign its values to the nodes
        ncols = len(table)
        csvtab = csv.reader(lines, delimiter=' ')
        for row in csvtab:
            if len(row)>ncols or len(row)<ncols:
                raise Exception(f"Number of header nodes does not match number of table columns: {ncols} != {len(row)}")
            for c in range(ncols):
                table[c].value_raw.append(row[c])
        # set additional node parameters
        nodes_new = []
        for node in table:
            nvalues = len(node.value_raw)
            node.dimension = [(nvalues,nvalues)]
            node.name = self.name + Sign.SEPARATOR + node.name
            node.indent = self.indent
            nodes_new.append(node)
        return nodes_new
