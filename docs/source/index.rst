ronto
#####

*Ronto* is a cli tool for building stuff using repotool, Yocto and Docker.
It is intended to simplify Yocto build environments and processes.

* It can be used by developers who just want to build a single recipe.
* It can also be used for headless CI builds or release builds covering a set
  of machines and images.
* All build activities can be transparently performed within a docker
  container or on bare metal.

*Ronto* is just the **ronto** command and it's sub-commands plus **ronto.yml**
control file located in the yocto project directory.

*Ronto* is the proposed prefix for 10^-27 of something.
It is like Yocto which is the prefix for 10^-24 of something.


.. toctree::
   :maxdepth: 2
   :numbered:
   :hidden:

   user/index
   architecture/index
   dev/index

Quick Start
===========

ronto is available on PyPI and can be installed with `pip <https://pip.pypa.io>`_.
Ronto requires python at version 3.5 or higher.

.. code-block:: console

    $ pip3 install ronto

After installing ronto the ronto command is available to you.

The build specification is maintained in a *ronto.yml*.

Start and explore with

.. code-block:: python

    # bootstrap a new build ronto.yml
    # -- not implemented yet --
    ronto bootstrap

    # fine grained step by step build
    ronto fetch
    ronto init
    ronto build
    # -- not implemented yet --
    ronto publish

    # or a custom command
    # -- not implemented yet --
    ronto run all