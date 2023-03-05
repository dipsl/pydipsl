import sys, os
import pytest
import numpy as np

sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'src'))
from dipsl import DIP, Environment
from dipsl.datatypes import IntegerType, FloatType, StringType, BooleanType
from dipsl.solvers import TemplateSolver

@pytest.fixture
def test_path():
    return "tests/examples/"

def test_example_of_use(test_path):

    with DIP() as dip:
        dip.code("""
        mpi
          nodes int = 36
          cores int = 96
        """)                               # get code from a string
        env1 = dip.parse()                 # parse the code

    with DIP(env1) as dip:                 # pass environment to a new DIP instance
        dip.load(test_path+"settings.dip") # add new parameter
        env2 = dip.parse()                 # parse new parameters

    nodes = env2.query("mpi.*")            # select nodes using a query
    geom = env2.request("?box.geometry")   # select a node using a request
    
    assert nodes[0].value == IntegerType(36)
    assert nodes[1].value == IntegerType(96)
    assert geom[0].value == IntegerType(3)

    data = env2.data(verbose=True)
    np.testing.assert_equal(data,{
        'mpi.nodes': 36,
        'mpi.cores': 96,
        'runtime.t_max': 10,
        'runtime.timestep': 0.01,
        'box.geometry': 3,
        'box.size.x': 10,
        'box.size.y': 3e7,
        'modules.heating': False,
        'modules.radiation': True,
    })

    data = env2.data(verbose=True, format="tuple")
    np.testing.assert_equal(data,{
        'mpi.nodes': 36,
        'mpi.cores': 96,
        'runtime.t_max': (10, 'ns'),
        'runtime.timestep': (0.01, 'ns'),
        'box.geometry': 3,
        'box.size.x': (10, 'nm'),
        'box.size.y': (3e7,'nm'),
        'modules.heating': False,
        'modules.radiation': True,
    })
    
    data = env2.data(verbose=True, format="type")
    np.testing.assert_equal(data,{
        'mpi.nodes':         IntegerType(36),
        'mpi.cores':         IntegerType(96),
        'runtime.t_max':     FloatType(10, 'ns'),
        'runtime.timestep':  FloatType(0.01, 'ns'),
        'box.geometry':      IntegerType(3),
        'box.size.x':        FloatType(10, 'nm'),
        'box.size.y':        FloatType(3e7, 'nm'),
        'modules.heating':   BooleanType(False),
        'modules.radiation': BooleanType(True),
    })
    
def test_definition_template(test_path):
    
    with DIP() as dip:
        dip.load(test_path+'definitions.dip')
        env3 = dip.parse()
        data = env3.data(format="type")
    np.testing.assert_equal(data,{
        'runtime.t_max':        FloatType(1e-08, 's'),
        'runtime.timestep':     FloatType(1e-11, 's'),
        'box.geometry':         IntegerType(3),
        'box.size.x':           FloatType(1e-06, 'cm'),
        'box.size.y':           FloatType(3.0, 'cm'),
        'box.size.z':           FloatType(23.0, 'cm'),
        'modules.hydrdynamics': BooleanType(True),
        'modules.heating':      BooleanType(False),
        'modules.radiation':    BooleanType(True)
    })
    with TemplateSolver(env3) as ts:
        text = ts.template(test_path+'template.txt', test_path+'processed.txt')
    assert text == "Geometry: 3\nBox size: [1e-06, 3.0, 23.0]\n"
