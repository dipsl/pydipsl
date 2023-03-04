Schema highliter
================

DIP schema highliter is design to highlight only most basic concepts of DIP language.
Definition of the schema highlighter is in file `lexer/DIP_Lexer_Schema.py`. Following block sumarizes all highliter posibilities.

.. code-block:: DIPSchema

   <indent><name> <type> = <value> <unit> # comment
   
   <indent>= <value> <unit>               # comment
   <indent>!options <value> <unit>        # comment
   <indent>!condition ('<expression>')      
   <indent>!condition ("<expression>")    # comment
   <indent>!condition ("""
   <expression>
   """)
   <indent>!format <value>
   <indent>!constant
   
   $source <name> = <path>

   {<source>?<query>}
   {<source>?<query>}[<slice>] 

   ("<expression>")
   ('<expression>')
   ("""
   <expression>
   """)
