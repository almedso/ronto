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

1. Developer builds locally on his machine a *one specific* package
   and deploys it to his *private development bare metal* target.

2. Integrator builds locally on his machine an image for two targets
   and deploy and tests to to integration targets.

3. Continuous Integration Server builds a set of images for a set of
   machines and publishes some images as well as all packages

4. A release engineer pins/releases a certain successful CI build

Requirements
------------

* This tool shall work with or without docker
* This tool shall work with and without repo tool.

This tool is just a convenient wrapper:
Yocto builds with or without this tool shall work the same way.


Concept
=======

Problems to be solved:

* support of docker environments | bare metal environments
* private repositories of sources (credential handling in docker)
* handling site.conf
* version pinning of integration releases
* Consistent CI/Releasing commit messages and tags (established conventions)
