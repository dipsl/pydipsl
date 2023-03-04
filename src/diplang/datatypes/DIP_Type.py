from pydantic import BaseModel
import numpy as np

class Type(BaseModel):
    value: str = None
    unit: str = None

    def __init__(self, value, unit=None, **kwargs):
        kwargs['value'] = value
        kwargs['unit'] = unit
        super().__init__(**kwargs)
    
