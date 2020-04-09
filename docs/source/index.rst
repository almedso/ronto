ronto
#####

*ronto* is a cli tool for building stuff using repotool, Yocto and Docker.

The *ronto* command is intended to simplify Yocto build environments and
processes.
It can be used by developers who just want to build a single
recipe.
It can also be used for headless CI builds or release builds covering a set of
machines and images.
All build activities can be transparently performed within a docker container
or on bare metal.

*ronto* is the proposed prefix for 10^-27 of something.
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

.. code-block:: console

    $ pip install ronto

After installing ronto the ronto command is available to you.

The build specification is maintained in a Rontofile.

Start and explore with

.. code-block:: python

    # bootstrap a new build Rontofile
    ronto bootstrap

    # fine grained step by step build
    ronto init
    ronto build
    ronto publish

    # or more compact round-trip
    ronto all
