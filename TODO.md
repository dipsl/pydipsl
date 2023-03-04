TODO List
=========

If box.geometry = 4, DIPL does not throw any exception:

  ```
  geometry int = {settings?box.geometry}
    = 1  # linear
    = 2  # cylindrical
    = 3  # spherical
  ```

Undefined nodes in referenced files throw error.
We need to allow modification to create genergic string nodes in referenced DIPL files.

  ``` # definition.dipl
  modules
    radiation bool
    {settings?modules.*}
  ```

  ``` # settings.dipl
  modules.radiation = bool
  ```

Import of units

  ```
  {<source>$<unit>} 
  ```