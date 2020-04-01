Rontofile Reference
===================

An example looks like this:

.. code ::

    # Environment variable defaults
    defaults:
      DL_DIR: ""
      SSTATE_DIR: ""
      WHITE_LIST_INJECT: ""
      PACKAGE_FEED_HOST: ""
    repo:
      url:
      manifest:
      branch:
    build:
      download: {{ DL_DIR }}
      shared_state: {{ SSTATE_DIR }}
      distro: {{
      inject: {{ WHITE_LIST_INJECT }}
      targets:
        - image: ams-image
          machine: roderigo
          publish: yes
        - image: ams-image
          machine: roderigo
          publish: yes
    publish:
      package_feed_host: {{ PACKAGE_FEED_HOST }}
      copy_base_url: {{ PUBLISH_BASE_URL }}