About DIP
=========

DIP is a minimalistic programming language that spetializes in parsing, managing and validation of dimensional initial parameters (DIP).
It was originally developed as a subproject to a proprietary code used in fusion physics.
Nevertheless, due to it's potential also in other code development, we publish it as an open-source module.

Numerical codes used in physics, astrophysics and engeneering usually depend on sets of compilation definitions, flags and initial settings.
Description of these parameters is often poorly documented and codes are prone to errors due to wrong input units and lack of proper parameter validation.
DIP is designed to adress these issues and provide a standardized and scalable interface between user and a code.
In the long run, DIP aims to become a standard tool for any numerical code and flatten the learning curve for end users.

Following features of DIP are already implemented in the current code version:

* parameter node definition, declaration and modification
* hierarchical structure of nodes
* value datatypes: boolean, integer, float, string
* parameter values: scalars, arrays, blocks and tables
* definitions of reference sources
* import of local/remote nodes
* injection of local/remote node values
* expressions
  
  * numerical for integer and float datatypes (with scalar values only)
  * logical for boolean datatypes
  * templates for string datatypes
* support for standard SI and CGS units
* definition of custom units
* automatic unit conversion during node modifications
* parameter validation: options, conditions, format and constants
* parameter branching using conditions
* syntax highlighter using "Pygments"

Current version of DIP is still in a beta stage.
Goles listed below are not implemented yet and need help from potential codevelopers:

* native implementation of DIP in C/C++ and Fortran
* numerical expressions support for calculations with arrays
* node values generated using native programming languages (C/C++, Fortran, Python)
* documentation generator and implementation into Sphinx

Any kind of help, collaboration, suggestions and further development of this project is hearthly welcommed.

DIP is published under MIT license. We kindly ask for a reference in projects that are based on this code.
