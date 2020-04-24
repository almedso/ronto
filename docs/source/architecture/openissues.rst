Open Issues
===========

Generate site.conf
------------------

Pro:
  - intelligent mapping between docker and none docker directories
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



.. code :: console

  ronto --env FOO=bar fetch
  ronto -eBAR=foo build

Pro:

* compose of own commands is better supported
* scripting is better since amount of site effects is minimized

Con:

* little more effort
