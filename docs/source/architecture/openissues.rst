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
