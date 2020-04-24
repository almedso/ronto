Preample
========

Yocto builds require a complex environment to run on.

Application developers, BSP developers, integration engineers,
release engineers have different needs to build something with
Yocto.

A lot of upstream input has to be maintained in terms of

* bblayers
* sources

Different quality attributes are applied like

* fast turn around time for app developers
* reproducibility for release engineers
* fast feedback for integrators

The output of Yocto builds is complex as well and is handle differently.


Build Process
-------------

0. Access the build host (login to bare metal machine or pick docker image)
1. Gather the build specification (layers, recipes, configuration)
2. Initialize the build environment (source an init script)
3. Pick a machine and an image/recipe and build
4. Use the build result (publish, run)

Gather build specification
..........................

Quite often upstream projects suggest using the Google repotool
to access bblayers available and maintained in git repositories.

Alternatively kas tool. - very good but a technology lock.

Gather build specification
..........................

Terminology
-----------

Developer build
    * Performed by a developer on a developers computer
    * Purpose is pure development, one build "small" target only

Verification build
    * Performed by a ci service on a headless computer
    * Fast feedback if the change/pull request might break master branch/trunk

Integration build
    * Performed by a ci service on a headless computer
    * Fast feedback if current state of integrated software still works
    * Provides latest integrated software in all variants

Integration release build
    * Performed by a ci service on a headless computer
    * Input is a pinned configuration
    * Provides reproducible and identifiable (by version) integrated software
      in all variants


Requirements
============

Use Cases
---------

Developer bootstraps Yocto build environment
............................................

.. code :: console

    ronto bootstrap

Developer has to answer a couple of questions.
Result is a created project directory plus a *ronto.yml*
inside the project directory.

Developer builds something on his machine
.........................................

Developer builds locally on his machine a *one specific* package
and deploys it to his *private development bare metal* target.

.. code :: console

    $ ronto build --fetch --init --interactive
    (yocto)> bitbake


Integrator builds locally
.........................

Integrator builds locally on his machine an image for two targets
and deploy and tests to to integration targets.

.. code :: console

    ronto --env TARGETS=mytargets.yml build --fetch --init


CI server builds and publishes
..............................

Continuous Integration Server builds a set of images for a set of
machines and publishes some images as well as all packages

.. code :: console

    ronto fetch
    ronto init --cleanconf
    ronto --env TARGETS=sources/recipe-repo/conf/integration-targets.yml build
    ronto --env TARGETS=sources/recipe-repo/conf/integration-targets.yml publish

Release Engineer releases
.........................

A release engineer pins/releases a certain successful CI build.
afterwards he/she build the pinned release.

    # do some pinning stuff
    ronto --env MANIFEST=release_xyz.yml fetch
    ronto init --cleanbuild
    ronto --env TARGETS=sources/recipe-repo/conf/release-targets.yml build
    ronto --env TARGETS=sources/recipe-repo/conf/release-targets.yml publish



Requirements
------------

* This tool shall work with or without docker
* This tool shall work with and without repo tool.

This tool is a convenient wrapper:
Yocto builds with or without this tool shall work the same way.


Quality Attributes
..................

* The project config file is the central play that should operate
  with references to details that are rather bound to recipes and configuration
  repositories.
* CLI and config file shall be self-explaining and intuitive
* Different pront colors (interactive if on docker/bare metal
* Different promt color if bitbake environment is active


Concept
=======

Problems to be solved:

* support of docker environments | bare metal environments
* private repositories of sources (credential handling in docker)
* handling site.conf
* version pinning of integration releases
* Consistent CI/Releasing commit messages and tags (established conventions)

Include of sub-rontofiles
-------------------------

Quality requirement: Maintainability

The build targets specification has to be located in the custom recipes repository.
Only in that repository are machines and images known.
Following the "strong coupling principle" the build targets specification must be
maintained in that repository as well.

.. note ::

   Late loading must be implemented, since it might be possible that this
   specification is only or updated available after the fetching step


Cleanup flags
-------------

E.g. in rontofile:

.. code :: yaml

    build:
      flags:
        - cleanconf
        - cleanbuild
        - cleansstate


Solution:
.........

Are part of init sub-command
can be customized into *ronto*scripts.


Command line variables
----------------------

Like reading from environment it is possibible to
read from command line (as global parameter)


Compose of own Commands
-----------------------

Allow custom commands (including options + injections)
like git config alias.xxx "blablub"

.. code :: yaml

   scripts:
     do-special:
       - '--env REPO=foo fetch'
       - '-f integrate.yml build'
       - '-f integrate.yml publish'

Pro:

* more flexibility to handle e.g. process specifics of
  integration builds or release builds
* support of customized developer workflows / development cycles

Con:

* more complexity

Solution:

* is implemented as proposed
  redesigned as run command and scripts section.


Multiple prioritized config files
---------------------------------

* Must be given at command line. Later on the command line implies
  higher priority.
* Items at higher priority overwrite items with lower priority.
  (same mechanism like css)

Pro:

* flexibility
* homogeneous handling
* little effort

Con:

* Overwrite rules are not super intuitive
* Concepts are not easily readable
* (like salt: Problem solving if you only have a hammer,
  everything turns a nail)

Solution:

* same thing is achived via extra "scripts" section, variable substituion,
  and include e.g. of target file.
