Open Issues
===========

Generate site.conf
------------------

Pro:
  - inteligent mapping between docker and none docker directories
  - no additional file to store
Con:
  - one more concept

.. code :: yaml

    ### -- Not implemented yet - still subject to evaluation --
    ## Generate build/conf/site.conf from values
    ## to do
    ## either with semantics for distro, upstream, download, sstate_cache
    ## or from list of define strings
    generate:
        download: "download"
        shared_state: "shared-state"
        distro: "{{ ams }}"


Cleanup flags
-------------

To clarify if overwrite on command line should be possible

.. code :: yaml

    build:
      flags:
        - cleanconf
        - cleanbuild
        - cleansstate

Command line variables
----------------------

Like reading from environment it is possibible to
read from command line (as global parameter)

.. code :: console

  ronto --env FOO=bar fetch
  ronto -eBAR=foo build

Pro:

* compose of own commands is better supported
* scripting is better since amount of site effects is minimized

Con:

* little more effort


Compose of own Commands
-----------------------

Allow custom commands (including options + injections)
like git config alias.xxx "blablub"

.. code :: yaml

   commands:
     do-special:
       - '-f integrate.yml fetch'
       - '-f integrate.yml build'
       - '-f integrate.yml publish'

Pro:

* more flexibility to handle e.g. process specifics of
  integration builds or release builds
* support of customized developer workflows / development cycles

Con:

* more complexity

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