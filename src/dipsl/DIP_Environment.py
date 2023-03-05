import numpy as np
from typing import List, Dict
from pydantic import BaseModel

from .DIP_Settings import *
from .datatypes import NumberType

class Environment(BaseModel):
    # Environment variables
    nodes: List    = []   # nodes
    units: List    = {}   # custom units
    sources: Dict  = {}   # custom reference sources

    # Reference on the current node
    autoref: str = None

    # Hierarchy list
    parent_indents: List[int] = [-1]  # indent level
    parent_names: List[str]   = []    # list of parent names

    # Case list
    case_counts: List[int]  = [0]     # case number in a current condition
    case_names: List[str]   = ['']    # condition case name
    
    def pop_node(self):
        """ Pop first node out of the node list
        """
        return self.nodes.pop(0)

    def prepend_nodes(self, nodes):
        """ Prepend new nodes to the node list
        """
        self.nodes = nodes + self.nodes
    
    def update_hierarchy(self, node, excluded):
        """ Register new node to the hierarchy

        :param node: Node that should be added
        :param list excluded: List of node keywords that should be excluded from the hierarchy
        """
        if node.name is not None and node.keyword not in excluded:
            while node.indent<=self.parent_indents[-1]:
                self.parent_indents.pop()
                self.parent_names.pop()
            self.parent_names.append(node.name)
            self.parent_indents.append(node.indent)
            node.name = SGN_SEPARATOR.join(self.parent_names)

    def is_case(self):
        """ Checks if outside or inside of a valid case clause
        """
        return not self.case_names[-1] or self.case_counts[-1]<2

    def _end_case(self):
        self.case_names.pop()
        self.case_counts.pop()
    
    def solve_case(self, node):
        """ Manage condition nodes

        :param node: Condition node
        """
        casename = self.case_names[-1]
        if node.name.endswith(SGN_CONDITION + KWD_CASE):
            if casename+KWD_CASE!=node.name:   # register new case
                self.case_names.append(node.name[:-4])
                self.case_counts.append(0)
            if node.value or self.case_counts[-1]==1:
                self.case_counts[-1] += 1
        elif node.name==casename + KWD_ELSE:
            self.case_counts[-1] += 1
        elif node.name==casename + KWD_END:    # end case using a keyword
            self._end_case()
        else:
            raise Exception(f"Invalid condition:", node.name)

    def prepare_node(self, node):
        """ Manage parameter nodes in a condition

        :param node: Parameter node
        """
        if not self.case_names[-1]: # outside of any condition
            return        
        if not node.name.startswith(self.case_names[-1]): # ending case at lower indent
            self._end_case()
        node.name = node.name.replace(
            SGN_CONDITION + KWD_CASE + SGN_SEPARATOR,''
        )
        node.name = node.name.replace(
            SGN_CONDITION + KWD_ELSE + SGN_SEPARATOR,''
        )

    def query(self, query:str, namespace:str="nodes"):
        """ Select local nodes according to a query

        :param str query: Node selection query
        :param str namespace: Query namespace (nodes, sources, or units)
        """
        if namespace=="nodes":
            nodes = []
            if query==SGN_WILDCARD:
                return [node.copy() for node in self.nodes]
            elif query[-2:]==SGN_SEPARATOR + SGN_WILDCARD:
                for node in self.nodes:
                    if node.name.startswith(query[:-1]):
                        node = node.copy()
                        node.name = node.name[len(query[:-1]):]
                        nodes.append(node.copy())
            else:
                for node in self.nodes:
                    if node.name==query:
                        node = node.copy()
                        node.name = node.name.split(SGN_SEPARATOR)[-1]
                        nodes.append(node.copy())
            return nodes
        elif namespace=="sources":
            if query==SGN_WILDCARD:   # return all sources
                return self.sources
            else:                     # return particular source
                if query not in self.sources:
                    raise Exception("Requested source does not exists:", query)
                return {query: self.sources[query]}
        elif namespace=="units":
            if query==SGN_WILDCARD:   # return all units
                return self.units
            else:                     # return particular unit
                if query not in self.units:
                    raise Exception("Requested unit does not exists:", query)
                return {query: self.units[query]}
        else:
            raise Exception("Invalid query namespace selected:", namespace)
        
    def request(self, path:str, count:int=None, namespace:str="nodes"):
        """ Request nodes from a path

        :param str path: Request path
        :param int count: Number of nodes that should be selected
        :param str namespace: Query namespace (nodes, sources, or units)
        """
        if self.autoref and path == SGN_QUERY: # reference type {?}
            filename,query = '', self.autoref
        elif SGN_QUERY in path:                    # reference type {source?query}
            filename,query = path.split(SGN_QUERY)
        else:                                      # reference type {source}
            filename,query = path,SGN_WILDCARD
        if filename:  # use external source to parse the values
            source =self.sources[filename]
            if isinstance(source, str):
                return source
            else:
                nodes = source.env.query(query, namespace)
        else:         # use values parsed in the current file
            if not self.nodes:
                raise Exception(f"Local nodes are not available for DIP import:", path)
            nodes = self.query(query, namespace)
        if count:
            if isinstance(count, list) and len(nodes) not in count:
                raise Exception(f"Path returned invalid number of nodes:", path, count, len(nodes))
            elif np.isscalar(count) and len(nodes)!=count:
                raise Exception(f"Path returned invalid number of nodes:", path, count, len(nodes))
        return nodes

    def data(self, verbose=False, format="value"):
        """ Return parsed values as a dictionary

        :param bool verbose: Display node values
        :param str format: Return data as values only, DIP datatypes, or tuples
        """
        data = {}
        for node in self.nodes:
            if format=="value":
                data[node.name] = node.value.value
            elif format=="type":
                data[node.name] = node.value
            elif format=="tuple":
                if isinstance(node.value, NumberType) and node.value.unit is not None:
                    data[node.name] = (node.value.value, node.value.unit)
                else:
                    data[node.name] = node.value.value
            else:
                raise Exception("Data format not recognized:", format)
            if verbose:
                 print(node.name,'|',node.indent,'|',node.keyword,'|',str(node.value),
                       '|',repr(node.units_raw), end='')
                 if hasattr(node,'options'):
                     if node.options:
                         print(' |',node.options, end='') 
                 print()
        return data
