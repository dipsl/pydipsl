import sys, os
import pytest
import numpy as np

sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'src'))
from dipsl import DIP
from dipsl.settings import Format
from dipsl.datatypes import FloatType, IntegerType, StringType

def parse(code):
    with DIP() as p:
        p.from_string(code)
        return p.parse().data(verbose=True,format=Format.TYPE)

def test_option():
    data = parse('''
coordinates int = 1
  = 1  # linear
  = 2  # cylindrical
  = 3  # spherical
    ''')
    np.testing.assert_equal(data,{
        'coordinates': IntegerType(1),
    })
    with pytest.raises(Exception) as e_info:
        parse("""
length float cm
  = 12 cm
  = 34 cm
        """)
    assert e_info.value.args[0] == "Node value must be defined:"
    with pytest.raises(Exception) as e_info:
        parse("""
deposition bool = true
  = true
  = false
        """)
    assert e_info.value.args[0] == "Node 'bool' does not support options"
    
def test_options():
    data = parse('''
size float cm
  !options [12,13,14,15,16] cm
  !options [22,23,24,25] m
size = 23 m
    ''')
    np.testing.assert_equal(data,{
        'size': FloatType(2300, 'cm')
    })
    with pytest.raises(Exception) as e_info:
        parse("""
size float cm
  !options [12,13,14,15,16] cm
size = 11
        """)
    assert e_info.value.args[0] == "Value 'FloatType(11.0 cm)' of node 'size' doesn't match with any option:"

def test_constant():
    data = parse('''
size float = 30 cm
  !constant
    ''')
    np.testing.assert_equal(data,{
        'size': FloatType(30, 'cm')
    })
    with pytest.raises(Exception) as e_info:
        parse("""
size float = 30 cm
  !constant
size = 23
        """)
    assert e_info.value.args[0] == "Node 'size' is constant and cannot be modified:"
    
def test_format():
    data = parse('''
name str = John
  !format "[a-zA-Z]+"
    ''')
    np.testing.assert_equal(data,{
        'name': StringType('John')
    })
    with pytest.raises(Exception) as e_info:
        parse("""
name str = 7-up
  !format '[a-zA-Z]+'
        """)
    assert e_info.value.args[0] == "Node value does not match the format:"
    with pytest.raises(Exception) as e_info:
        parse("""
size float = 23 cm
  !format '[a-zA-Z]+'
        """)
    assert e_info.value.args[0] == "Format can be set only to string nodes"

def test_condition():
    data = parse('''
size float = 23 cm
  !condition ('200 mm < {?} && {?} < 30 cm')
    ''')
    np.testing.assert_equal(data,{
        'size': FloatType(23, 'cm')
    })
    with pytest.raises(Exception) as e_info:
        parse("""
size float = 23 cm
  !condition ('250 mm < {?} && {?} < 30 cm')
        """)
    assert e_info.value.args[0] == "Node does not fullfil a condition:"
