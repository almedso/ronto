Developers Guide
################

.. include:: ../../../CONTRIBUTING.rst


.. _testing-label:

Testing
=======

The ronto project implements a regression
test suite that improves developer productivity by identifying capability
regressions early.

Developers implementing fixes or enhancements must ensure that they have
not broken existing functionality. The ronto
project provides some convenience tools so this testing step can be quickly
performed.

Developer **unit tests** are supported with *py.test* as well
as **component tests** are supported with *behave*.

The **unit tests** are specified in the *tests* folder.
The **component tests** are specified in the *features* folder.

Use the Makefile convenience rules to run the tests.

.. code-block:: console

    (venv) $ make test

To run tests verbosely use:

.. code-block:: console

    (venv) $ make test-verbose

Alternatively, you may want to run the tests suites directly. The following
steps assume you are running in a virtual environment in which the
``ronto`` package has been installed. If this is
not the case then you will likely need to set the ``PYTHONPATH`` environment
variable so that the ``ronto`` package can be found.

.. code-block:: console

    (venv) $ py.test  # unit tests
    (venv) $ behave  # component tests


.. _style-compliance-label:

Code Style
==========

Adopting a consistent code style assists with maintenance. This project uses
the code style formatter called Black. A Makefile convenience rule to enforce
code style compliance is available.

.. code-block:: console

    (venv) $ make style


.. _annotations-label:

Type Annotations
================

The code base contains type annotations to provide helpful type information
that can improve code maintenance.

Use the Makefile convenience rule to check no issues are reported.

.. code-block:: console

    (venv) $ make check-types


.. _documentation-label:

Documentation
=============

To rebuild this project's documentation, developers should use the Makefile
in the top level directory. It performs a number of steps to create a new
set of `sphinx <http://sphinx-doc.org/>`_ html content.

.. code-block:: console

    (venv) $ make docs

To quickly check consistency of ReStructuredText files use the dummy run which
does not actually generate HTML content.

.. code-block:: console

    (venv) $ make check-docs

To quickly view the HTML rendered docs, start a simple web server and open a
browser to http://127.0.0.1:8000/.

.. code-block:: console

    (venv) $ make serve-docs


.. _release-label:

Versioning
==========

This project is a command line tool.
Semantic versioning is applied and interpreted as follow:

* major change: New commands, new ronto.yml version - or just something
    important
* minor change: Additional options, additional fields in ronto.yml
    no behavior change.
* patch change: Same behavior, bug-fixes applied

Versions with major equal to zero imply an expectation of sematic instability
in cli and ronto file.

Release Process
===============

The following steps are used to make a new software release.

The steps assume they are executed from within a development virtual
environment.

- Check that the package version label in ``__init__.py`` is correct.

- Create and push a repo tag to Github.

  .. code-block:: console

      $ git checkout master
      $ git tag vMajor.Minor.Patch -m "A meaningful release tag comment"
      $ git tag  # check release tag is in list
      $ git push --tags origin master

  - This will trigger Github to create a release at:

    ::

        https://github.com/{username}/ronto/releases/{tag}

- Create the release distribution. This project produces an artefact called a
  pure Python wheel. The wheel file will be created in the ``dist`` directory.

  .. code-block:: console

      (venv) $ make dist

- Test the release distribution. This involves creating a virtual environment,
  installing the distribution into it and running project tests against the
  installed distribution. These steps have been captured for convenience in a
  Makefile rule.

  .. code-block:: console

      (venv) $ make dist-test

- Upload the release to PyPI using

  .. code-block:: console

      (venv) $ make dist-upload

  The package should now be available at https://pypi.org/project/ronto/
