ronto
#####

Wrapper around building stuff using repotool and Yocto.

``ronto`` is the proposed prefix for 10^-27 of something.
It is like Yocto which is the prefix for 10^-24 of something.

.. toctree::
   :maxdepth: 2
   :numbered:
   :hidden:

   user/index
   architecture/index
   dev/index
   api/modules


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
