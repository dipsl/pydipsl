import sys, os
import pytest
import numpy as np
from math import isclose

sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'src'))
from diplang import DIP, Unit
from diplang.solvers import UnitSolver
from diplang.datatypes import FloatType, StringType

def parse(code):
    with DIP() as p:
        p.code(code)
        return p.parse().data(verbose=True,format="type")

def test_conditions():
    data = parse("""
    units str = 'cgs'
    @case ("{?units} == 'cgs'")
      $unit L = 1 cm
      $unit M = 1 g
      $unit T = 1 s
    @case ("{?units} == 'mks'")
      $unit L = 1 m
      $unit M = 1 kg
      $unit T = 1 s
    @end
    energy float = 1 eV
    energy = 1 [M]*[L]2/[T]2  # in CGS units this is erg
    """)
    np.testing.assert_equal(data,{
        'units':  StringType('cgs'),
        'energy': FloatType(6.241506363094028e+11, 'eV'),
    })
    
def test_declaration():
    data = parse("""
    # define cgs unit base
    $unit length = 1 cm
    $unit mass = 1 g
    $unit time = 1 s

    energy float = 1 eV
    energy = 1 [mass]*[length]2/[time]2  # in CGS units this is erg
    """)
    np.testing.assert_equal(data,{
        'energy': FloatType(6.241506363094028e+11, 'eV'),
    })
    with pytest.raises(Exception) as e_info:
        parse("""
        $unit e = 1 cm
        $unit e = 1 cm
        """)
    assert e_info.value.args[0] == "Following unit already exists:"

def test_unit_inject():
    data = parse("""
    mass float = 1 kg
    $unit M = {?mass}
    weight float = 80 [M]
    """)
    np.testing.assert_equal(data,{
        'mass': FloatType(1, 'kg'),
        'weight': FloatType(80, '[M]')
    })
    
def test_unit_import():
    data = parse("""
    $source file = tests/blocks/nodes.dip
    $unit {file?energy}
    energy float = 8 [energy]
    energy = 1 J
    """)
    np.testing.assert_equal(data,{
        'energy': FloatType(1e7, '[energy]')
    })
    data = parse("""
    $source file = tests/blocks/nodes.dip
    $unit {file?*}
    energy float = 8 [energy]
    energy = 1 J
    """)
    np.testing.assert_equal(data,{
        'energy': FloatType(1e7, '[energy]')
    })
    with pytest.raises(Exception) as e_info:
        parse('''
    $source file = tests/blocks/nodes.dip
    $unit {file?mass}
        ''')
    assert e_info.value.args[0] == "Requested unit does not exists:"
    with pytest.raises(Exception) as e_info:
        parse('''
    $source energy = tests/blocks/nodes.dip
    $unit energy = 1 J
    weight float = 8 [energy]
    $unit {energy?energy}
        ''')
    assert e_info.value.args[0] == "Reference unit alread exists:"
    
def test_base():
    with UnitSolver() as p:
        # Closure of base units
        unit = Unit(1.0)
        for base in p.base.values():
            unit = unit * base
        print(f"Base: {unit.num} {unit.base}")
        assert unit == Unit(1.0, [1 for i in range(p.nbase)])

def test_operations():
    with UnitSolver() as p:
        # Multiplication
        unit1 = Unit(2.0, [i for i in range(1,1+p.nbase)])
        unit2 = Unit(2.0, [i for i in range(2,2+p.nbase)])
        unit3 = unit1 * unit2
        unit4 = Unit(unit1.num*unit2.num,
                          [unit1.base[i]+unit2.base[i] for i in range(p.nbase)])
        print(f"  {unit1.num} {unit1.base}\n* {unit2.num} {unit2.base}\n= {unit3.num} {unit3.base}\n")
        assert unit3 == unit4
        # Division
        unit1 = Unit(4.0, [i+i for i in range(1,1+p.nbase)])
        unit2 = Unit(2.0, [i for i in range(1,1+p.nbase)])
        unit3 = unit1 / unit2
        unit4 = Unit(unit1.num/unit2.num,
                          [unit1.base[i]-unit2.base[i] for i in range(p.nbase)])
        print(f"  {unit1.num} {unit1.base}\n/ {unit2.num} {unit2.base}\n= {unit3.num} {unit3.base}\n")
        assert unit3 == unit4
        # Power
        unit1 = Unit(2.0, [i for i in range(1,1+p.nbase)])
        power = 3
        unit2 = unit1 ** power
        unit3 = Unit(unit1.num**power, [unit1.base[i]*power for i in range(p.nbase)])
        print(f"  {unit1.num} {unit1.base}\n^ {power}\n= {unit3.num} {unit3.base}")
        assert unit2 == unit3
        
def test_units():
    with UnitSolver() as p:
        units = {
            'm':     p.units['m'],                               # just a unit                      
            'm-2':   p.units['m']**-2,                           # exponents
            'mm':    p.prefixes['m'] * p.units['m'],             # prefixes
            'km2':   (p.prefixes['k'] * p.units['m'])**2,        # all together
            'uOhm3': (p.prefixes['u'] * p.units['Ohm'])**3,      # units with long names
            '[pi]':  p.units['[pi]'],                            # number pi
            '[e]':   p.units['[e]'],                             # electronvolt
        }
        for name, unit2 in units.items():
            unit1 = p.unit(name)
            print("%-05s"%name, f"{unit1.num:.03e} {unit1.base}")
            assert unit1 == unit2

def test_expressions():
    with UnitSolver() as p:
        newton = p.prefixes['k'] * p.base['g']
        newton = newton * p.base['m']
        newton = newton / p.base['s']**2
        units = {
            'N':   'kg*m/s2',        # basic operations
            'Pa':  'kg/(s2*m)',      # parentheses in denominator
            'J':   '(kg*m2)/s2',     # parentheses in nominator
            'W':   'kg*(m2/s3)',     # fraction in parentheses
            'A':   'C*s-1',          # negative exponents
            'V':   'kg*(m2/(s2*C))', # nested parentheses
            'Ohm': '((kg*m2)/s)/C2', # multiple fractions with parentheses
            'S':   's*C2/kg/m2',     # multiple fractions without parentheses
            'deg': '2*[pi]*rad/360', # numbers and constants
        }
        for name, expr in units.items():
            unit1 = p.units[name]
            unit2 = p.solve(expr)
            print("%-03s %-15s"%(name,expr), "%.03e"%unit1.num, unit1.base)
            assert unit1 == unit2

def test_derivates():
    # Check if derived units are correct
    with UnitSolver() as p:
        for sign, unit in p.derivates.items():
            if not unit.dfn:
                continue
            expr = p.solve(unit.dfn)
            #print("%-13s"%unit.name, "%-4s"%sign, "%-15s"%unit.dfn,
            #      "%.06f"%expr.num, expr.base)
            equal = expr == unit
            if not equal:
                print(f"Expr.: {expr.num:.6f} {expr.base}")
                print(f"Unit:  {unit.num:.6f} {unit.base}")
            assert equal
            
def test_convert():
    examples = [
        (1,   'm',    1e-3,          'km'),
        (1,   'kJ',   1e3,           'J'),
        (1,   'eV',   1.6021773e-4,  'fJ'),
        (1,   'erg',  624.150636,    'GeV'),
        (1,   'deg',  0.01745329,    'rad'),
        (1,   'Cel',  274.15,        'K'),
        (1,   'kCel', 1273.15,       'K'),
        (1e3, 'K',    726.85,        'Cel'),
        (1,   'kK',   0.72685,       'kCel'),
    ]
    for (value1,expr1,value2,expr2) in examples:
        print(f"{value1:.3e} {expr1:4s} = {value2:.3e} {expr2}")
        value = FloatType(value1, expr1)
        value.convert(expr2)
        equal = isclose(value.value, value2, rel_tol=1e-6)
        if not equal:
            print(f"Value 1 given:     {value1:.3e} {expr1}")
            print(f"Value 2 converted: {value.value} {expr2}")
            print(f"Value 2 expected:  {value2} {expr2}")
        assert equal
            
if __name__ == "__main__":
    # Specify wich test to run
    test = sys.argv[1] if len(sys.argv)>1 else True

    # Loop through all tests
    for fn in dir(sys.modules[__name__]):
        if fn[:5]=='test_' and (test is True or test==fn[5:]):
            print(f"\nTesting: {fn}\n")
            locals()[fn]()
