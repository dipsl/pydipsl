Example of use
==============

The main implementation of DIP is written in Python.
For implementations in other languages look into corresponding documentations.

A first step to parse a DIP code is to import its main class ``DIP``.

.. code-block:: python

   from diplang import DIP
   
Multiple code sources (from strings, or files) can be loaded and combined into one parameter list.
Files containing DIP code should have an extention ``.dip``, otherwise they will be interpreted as normal text files.

.. code-block:: DIP
   :caption: settings.dip

   runtime
     t_max float = 10 ns
     timestep float = 0.01 ns

   box
     geometry int = 3
     size
       x float = 10 nm
       y float = 3e7 nm

   modules
     heating bool = false
     radiation bool = true

Parsing DIP code
----------------
     
It is recommendet to create DIP objects using ``with`` statement.

.. code-block:: python

   with DIP() as dip:            # create DIP object
       dip.code("""           
       mpi
	 nodes int = 36
	 cores int = 96
       """)                      # get code from a string
       env1 = dip.parse()        # parse the code

Parsed nodes, sources and units are stored in an environment object of class ``Environment``. This object can be easily transferred into a new instance of ``DIP`` and immediatelly used without additional parsing. 

.. code-block:: python

   with DIP(env1) as dip:              # pass environment to a new DIP instance
       dip.load("settings.dip")        # add new parameter
       env2 = dip.parse()              # parse new parameters

Getting parsed data
-------------------
       
Particular nodes can be selected using :doc:`references <../syntax/references>`.

.. code-block:: python
       
   nodes = env2.query("mpi.*")            # select nodes using a query method
   geom = env2.request("?box.geometry")   # select a node using a request method

In the example above variable ``nodes`` is a list of two nodes: ``mpi.nodes`` and ``mpi.cores``.
Variable ``geom`` is a list with only one node ``box.geometry`` that was loaded from file ``settings.dip``.

All environmental data can be parsed as a dictionary.

.. code-block::

   # Values are returned as Python datatypes
   data = env2.data()

   # data = {
   #     'mpi.nodes': 36,
   #     'mpi.cores': 96,
   #     'runtime.t_max': 10,
   #     'runtime.timestep': 0.01,
   #     'box.geometry': 3,
   #     'box.size.x': 10,
   #     'box.size.y': 3e7,
   #     'modules.heating': False,
   #     'modules.radiation': True,
   # }

   # Same as above, but umbers with units are returned as tuples
   data = env2.data(format="tuple")

   # data = {
   #     'mpi.nodes': 36,
   #     'mpi.cores': 96,
   #     'runtime.t_max': (10, 'ns'),
   #     'runtime.timestep': (0.01, 'ns'),
   #     'box.geometry': 3,
   #     'box.size.x': (10, 'nm'),
   #     'box.size.y': (3e7,'nm'),
   #     'modules.heating': False,
   #     'modules.radiation': True,
   # }
   
   # Values are returned as DIP datatypes
   data = env2.data(format="type")

   # data = {
   #     'mpi.nodes': IntegerType(36),
   #     'mpi.cores': IntegerType(96),
   #     'runtime.t_max': FloatType(10, 'ns'),
   #     'runtime.timestep': FloatType(0.01, 'ns'),
   #     'box.geometry': IntegerType(3),
   #     'box.size.x': FloatType(10, 'nm'),
   #     'box.size.y': FloatType(3e7, 'nm'),
   #     'modules.heating': BooleanType(False),
   #     'modules.radiation': BooleanType(True),
   # }

   # Values are returned as tuples
   
