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
    
def test_inline_matrix():
    with DIP() as p:
        p.from_string('''
velocity int[1:,3] = """
[[42,34,35],
 [23,34,64],
 [35,23,23]]
""" km/s
        ''')
        env = p.parse()
    np.testing.assert_equal(env.data(verbose=True,format=Format.TYPE),{
        'velocity': IntegerType([[42,   34,   35],[ 23,   34,  64],[ 35, 23,  23]], 'km/s'),
    })

def test_inline_table():
    data = parse('''
outputs table = """
time float s
snapshot int
intensity float W/m2

0.234 0 2.34
1.355 1 9.4
2.535 2 3.4
3.255 3 2.3
4.455 4 23.4
  """  # endqotes can be indented
    ''')
    np.testing.assert_equal(data,{
        'outputs.time': FloatType([0.234, 1.355, 2.535, 3.255, 4.455], 's'),
        'outputs.snapshot': IntegerType([0, 1, 2, 3, 4]),
        'outputs.intensity': FloatType([ 2.34,  9.4 ,  3.4 ,  2.3 , 23.4 ], 'W/m2'),
    })

    
def test_inline_text():
    data = parse('''
text str = """
   tripple qotes # ' " \' \"
block of text
""" 
    ''')
    np.testing.assert_equal(data,{
        'text': StringType('   tripple qotes # \' " \' "\nblock of text')
    })
        
if __name__ == "__main__":
    # Specify wich test to run
    test = sys.argv[1] if len(sys.argv)>1 else True

    # Loop through all tests
    for fn in dir(sys.modules[__name__]):
        if fn[:5]=='test_' and (test is True or test==fn[5:]):
            print(f"\nTesting: {fn}\n")
            locals()[fn]()
