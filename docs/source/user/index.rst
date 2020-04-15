User Guide
##########

.. _install-guide-label:

Installation and Dependencies
=============================

``ronto`` requires python3, specifically python3.5+.

The simplest way to install ronto is using Pip.

.. code-block :: bash

    $ pip3 install ronto

This will install ``ronto`` and all of its dependencies.

Usage
=====

The usage is very simple. There is just the command **ronto**
with sub-commands for the different specific tasks.

The **ronto** command reveals what it is capable by running:

.. code-block ::  bash

    $ ronto --help

or if you need help to one of the sub command call:

.. code-block ::  bash

    $ ronto <subcommand> --help


Be aware that there are global options like *--verbose* or
*--dryrun* that must be given right after the **ronto** command
whereby the sub-commands can have sub-command specific options.

The **ronto** command is expected to be called in the yocto project
root directory. It operates based on configuration in a **ronto.yml**.
That **ronto.yml** is supposed to be located in the very same directory.
An alternative **ronto.yml** can be given by *-f* or *--file*
global option.

.. include:: rontofile.rst

.. include:: ../../../CHANGELOG.rst

.. _report-bugs-label:

Report Bugs
===========

Report bugs at the `issue tracker <https://github.com/almedso/ronto/issues>`_.

Please include:

  - Operating system name and version.
  - Any details about your local setup that might be helpful in troubleshooting.
  - Detailed steps to reproduce the bug.
