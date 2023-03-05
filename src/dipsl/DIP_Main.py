import numpy as np
import re
import os
from typing import List
from pydantic import BaseModel

from .DIP_Environment import Environment
from .DIP_Unit import Unit
from .settings import Keyword, Sign
from .nodes.DIP_Parser import Parser
from .nodes import EmptyNode, ImportNode, UnitNode, SourceNode, CaseNode
from .nodes import OptionNode, ConstantNode, FormatNode, ConditionNode
from .nodes import ModNode, GroupNode
from .nodes import BooleanNode, IntegerNode, FloatNode, StringNode, TableNode
from .solvers import LogicalSolver
from .datatypes import Type

class DIP(BaseModel):
    """ DIP parser class

    :param str code: DIP code
    :param DIP_Environment env: DIP environment object
    """
    env: Environment
    lines: List[str] = []
    source: str = 'inline'

    def __init__(self, env:Environment=None, **kwargs):
        if env:
            kwargs['env'] = env
        elif 'env' not in kwargs:
            kwargs['env'] = Environment()
        super().__init__(**kwargs)

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass
        
    def from_file(self, filepath:str):
        """ Load DIP code from a file

        :param str filepath: Path to a DIP file
        """
        self.source = filepath
        with open(filepath,'r') as f:           
            self.lines += f.read().split('\n')

    def from_string(self, code:str):
        """ Use DIP code from a string

        :param str code: DIP code
        """
        self.source = 'inline'
        self.lines += code.split('\n')

    def add_source(self, name:str, path:str):
        self.lines += [f"{Sign.VARIABLE}{Keyword.SOURCE} {name} = {path}"]
        
    def add_unit(self, name:str, value:float, unit:str=None):
        if unit:
            self.lines += [f"{Sign.VARIABLE}{Keyword.UNIT} {name} = {value} {unit}"]
        else:
            self.lines += [f"{Sign.VARIABLE}{Keyword.UNIT} {name} = {value}"]

    def parse(self):
        """ Parse DIP nodes from code lines
        """
        # Convert code lines to nodes
        l = 0
        env = Environment()
        while len(self.lines)>0:
            l, line = l+1, self.lines.pop(0)
            # Group block structures
            if '"""' in line:
                block = []
                while len(self.lines)>0:
                    l, subline = l+1, self.lines.pop(0)
                    if '"""' in subline:
                        line += "\n".join(block) + subline.lstrip()
                        break
                    else:
                        block.append( subline )
                else:
                    raise Exception("Block structure starting on line %d is not properly terminated."%l)
            node = self._determine_node(line, l, self.source)
            env.nodes.append(node)
        # Parse nodes
        while len(env.nodes):
            node = env.pop_node()
            # Perform specific node parsing only outside of case or inside of valid case
            if self.env.is_case():
                node.inject_value(self.env)
                parsed = node.parse(self.env)
                if parsed: 
                    # Add parsed nodes to the queue and continue
                    env.prepend_nodes(parsed)
                    continue
            # Create hierarchical name
            excluded = ['empty','unit','source',
                        'option','constant','format','condition']
            self.env.update_hierarchy(node, excluded)
            # Add nodes to the list
            excluded += ['group']
            if node.keyword in excluded:
                continue
            elif node.keyword=='case':   # Parse cases
                self.env.solve_case(node)
            else:
                if not self.env.is_case():
                    continue
                self.env.prepare_node(node)
                # Set the node value
                node.set_value()
                # If node was previously defined, modify its value
                for n in range(len(self.env.nodes)):
                    if self.env.nodes[n].name==node.name:
                        if self.env.nodes[n].constant:
                            raise Exception(f"Node '{self.env.nodes[n].name}' is constant and cannot be modified:",node.code)
                        self.env.nodes[n].modify_value(node, self.env)
                        break
                # If node wasn't defined, create a new node
                else:
                    if node.keyword=='mod':
                        raise Exception(f"Modifying undefined node:",node.name)
                    self.env.nodes.append(node)
        # Validate nodes
        for node in self.env.nodes:
            # Check if all declared nodes have assigned value
            if node.defined and node.value is None:
                raise Exception(f"Node value must be defined:", node.code)
            # check if node value is in options
            if node.keyword!='bool' and node.options:
                if node.value not in node.options:
                    if isinstance(node.value, Type):
                        raise Exception(f"Value '{str(node.value)}' of node '{node.name}' doesn't match with any option:", node.options)
                    else:
                        raise Exception(f"Value '{node.value}' of node '{node.name}' doesn't match with any option:", node.options)
            # Check conditions
            if node.keyword in ['float','int']  and node.condition:
                env=self.env.copy()
                env.autoref = node.name
                with LogicalSolver(env) as s:
                    if not s.solve(node.condition):
                        raise Exception("Node does not fullfil a condition:",
                                        node.name, node.condition)
            # Check formats if set for strings
            if node.keyword=='str' and node.format:
                m = re.match(node.format, node.value.value)
                if not m:
                    raise Exception("Node value does not match the format:",
                                    node.value.value, node.format)
        return self.env
        
    def _determine_node(self, code, line, source):
        # Add replacement marks
        # TODO: we need to also properly treate arrays like this ["d#", "b"]
        encode = ["\\'", '\\"', "\n"]
        for i,symbol in enumerate(encode):
            code = code.replace(symbol,f"$@{i:02d}")
            
        # Determine node type
        parser = Parser(
            code=code,
            line=line,
            source=source
        )
        steps = [
            EmptyNode.is_node,            # parse empty line node
            parser.part_indent,           
            ImportNode.is_node,           # parse root import directive
            UnitNode.is_node,             # parse unit directive
            SourceNode.is_node,           # parse source directive
            CaseNode.is_node,             # parse case directive
            OptionNode.is_node,           # parse option setting
            ConstantNode.is_node,         # parse constant setting
            FormatNode.is_node,           # parse format setting
            ConditionNode.is_node,        # parse condition setting
            parser.part_name,             
            GroupNode.is_node,            # parse group node
            ImportNode.is_node,           # parse group import directive
            ModNode.is_node,              # parse modification
            parser.part_type,             
            BooleanNode.is_node,          # parse boolean node
            IntegerNode.is_node,          # parse integer node
            FloatNode.is_node,            # parse float node
            StringNode.is_node,           # parse string node
            TableNode.is_node,            # parse table node
        ]
        node = None
        for step in steps:
            if step.__name__=='is_node':
                node = step(parser)
                if node:
                    node = node
            else:
                step()
            if node and parser.is_empty():
                break
        else:
            raise Exception(f"Incorrect format: {code}")
        
        # Convert symbols to original letters
        def decode_symbols(value):
            replace = ["\'", '\"', "\n"]
            if isinstance(value, (list, np.ndarray)):
                value = [decode_symbols(v) for v in value]
            elif value is None:
                return value
            else:
                for i,symbol in enumerate(replace):
                    value = value.replace(f"$@{i:02d}", symbol)
            return value
        
        # Remove replacement marks
        if node.value_expr:
            node.value_expr = decode_symbols(node.value_expr)
        node.value_raw = decode_symbols(node.value_raw)
        node.code = decode_symbols(node.code)

        # Return proper node type
        return node
