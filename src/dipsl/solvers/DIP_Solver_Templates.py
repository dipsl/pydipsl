import numpy as np
from pydantic import BaseModel

from ..DIP_Environment import Environment
from ..nodes.DIP_Parser import Parser
from ..datatypes import Type
from ..DIP_Settings import *

class TemplateSolver(BaseModel):

    env: Environment

    def __init__(self, env:Environment=None, **kwargs):
        if env:
            kwargs['env'] = env
        else:
            kwargs['env'] = Environment()
        super().__init__(**kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass
    
    def solve(self, expr):
        out = ''
        kwargs = {'line':0, 'source': 'template', 'keyword':'expr'}
        while len(expr)>0:
            sign, expr = expr[0], expr[1:]
            if sign=='{':
                p = Parser(code=expr, **kwargs)
                p.part_reference()
                p.part_slice()
                p.part_format()
                if p.value_ref and p.ccode[0]=='}':
                    nodes = self.env.request(p.value_ref, count=1)
                    if p.value_slice:
                        value = nodes[0].slice_value(p.value_slice)
                    else:
                        value = nodes[0].value
                    if isinstance(value, Type):
                        value = value.value
                    if p.formating:
                        form = "{0"+p.formating+"}"
                        out += form.format(value)
                    else:
                        out += str(value)
                    expr = p.ccode[1:]
                else:
                    out += sign
            else:
                out += sign
        return out

    def template(self, file_in, file_out=None):
        with open(file_in,'r') as f:
            template = f.read()
        text = self.solve(template)
        if file_out:
            with open(file_out,'w') as f:
                f.write(text)
        return text
            
