from typing import Union, List
import numpy as np

from .DIP_Type import Type

class BooleanType(Type):
    value: Union[bool,list]
    dtype = bool

    def __str__(self):
        return f"BooleanType({self.value})"
    
    def __init__(self, value, **kwargs):
        kwargs['value'] = value
        if isinstance(kwargs['value'], np.ndarray):
            kwargs['value'] = kwargs['value'].tolist()
        super().__init__(**kwargs)
