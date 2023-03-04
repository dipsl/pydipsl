from typing import List
from pydantic import BaseModel

class NodeBase(BaseModel):
    code: str 
    line: int = None
    source: str = None
    keyword: str = None
    dtype = str
    indent: int = 0
    name: str = None
    value_raw: str = None
    value_ref: str = None
    value_expr: str = None
    value_slice: List[tuple] = None
    units_raw: str = None
    defined: bool = False
    dimension: List[tuple] = None
    options: List[BaseModel] = None  
