import sys
sys.path.append("../src")

from diplang import DIP
from diplang.solvers import TemplateSolver

with DIP() as dip:
    dip.load('./definitions.dip')
    dip.parse()
    print("")
    print("Parsed nodes:")
    for name,value in dip.env.data().items():
        print(name, value)
    print("")
