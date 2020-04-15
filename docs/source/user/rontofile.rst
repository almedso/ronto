Rontofile Reference
===================

The ronto file named *ronto.yml* is the home of ronto settings.
This name *ronto.yml* plus the location in the root directory
of the (Yocto) project is established as convention.
It enforces two things:

* Projects are operated from this directory and as long as
  the those conventions are maintained experienced developers and
  integrators find themselves "at home" quickly.
* One save time in providing additional parameters on the command line.
  Thus, less tiny typing errors can be made.

Rontofile content
-----------------

The following full blown *ronto.yml* including documentation shows the
maximum capabilities and explains the meaning of those single values.

Yaml format is used to arrange and express the settings.
See `Wikipedia <https://en.wikipedia.org/wiki/YAML>`_ for introduction
and `Yaml home <https://yaml.org/spec/1.2/spec.html>`_ for formal specification.

If an obvious content line is commented out, this means the given value
is taken as a default. There is no need to have this setting part of
the *ronto.yml*, it will assemble a compact presentation.

Build Source Specification
..........................

Build sources (or configuration sources or just sources) are all
Yocto layers, classes, recipes and configurations needed to build something
using Yocto. The *ronto* tool allows to specify

* nothing - it is up to manual configuration out of scope from *ronto*.
* a set of git repositories - *ronto* supports initial cloning only.
* a manifest repository - *ronto* invokes google repo tool to init and sync.

A mix is possible although not really recommended.

.. code :: yaml

    ## if repo is set the google repo tool is used to pull sources from
    ## upstream and locally. It requires the repo tool installed.
    ## the url parameter is mandatory.
    repo:
      url: git@github.com:group/manifest-repo.git  ## replace by your url
      ## optional manifest default is default.xml
      manifest: default.xml
      ## optional branch default is master
      branch: master

    ## If repo is not used: Alternative source definition is via repo.
    ## Only if not locally available yet the sources are pulled
    ## If a source directory is available no update is performed
    git:
      ## in case the list of git repositories is empty the following (poky)
      ## is picked as a default
      - source_dir: sources/poky  # this entry is used if the list is empty
        git_url: git://git.yoctoproject.org/poky  # same here
      ## more than one repository are possible like below
      - source_dir: sources/meta-openembedded
        git_url: https://github.com/openembedded/meta-openembedded

Build Processing Specification
..............................

This section clarifies how configuration files (local.con, bblayers.conf,
site.conf) are created/updated, how the build directory structure looks like
as well as what kind of clean is applied before building.

.. code :: yaml

    ## The build section
    build:
      ## The init script needs to be sourced to prepare the environment to
      ## run bitbake. The default poky script is used if nothing is given
      init_script: sources/poky/oe-init-build-env

      ## if not set no template dir is injected and the defaults from poky are
      ## used. This is the place to inject custom local.conf(.sample) and
      ## custom bblayers.conf(.sample)
      template_dir: sources/poky/meta-poky/conf

      ## If not set the default "build" as specified in the poky init script is
      ## used. Most likely it is not subject to change.
      build_dir: build

      ## site.conf is used to establish site specific settings
      ## There are different strategies to deal with
      ## If not given site.conf is ignored.
      site:
        ## Default behavior is conservative. if a site.conf file exists in
        ## build/conf directory it is left untouched.
        ## if it is not available it is created by file/generated settings
        ## if overwrite is given site.conf is always overwritten
        ## in build/conf directory
        overwrite: false

        ## Use a file to establish build/conf/site.conf
        ## if nothing else is given file is the default strategy to establish
        ## site.conf
        file: site.conf  ## path is relative to project root directory

Build Targets
.............

Build targets are best defined in the meta layer where machines and images
are defined. This is where they belong to.

.. code :: yaml

    targets:
      - image: ams-image
        machine: roderigo
        publish: yes
      - image: ams-image
        machine: roderigo
        publish: yes


Publishing
..........

.. code :: yaml

    ## -- Not implemented yet --
    ## Package publishing
    publish:
      host_directory: xxx
      package_feed_host: {{ PACKAGE_FEED_HOST }}
      copy_base_url: {{ PUBLISH_BASE_URL }}

Using Docker
............

*ronto* is capable to delegate all builds to a docker container, running
a docker image with Yocto prerequisites installed.
*ronto* takes over container management (image download, creation),
container startup and volume injection and build execution transparently.

.. code :: yaml

    ## docker is a toplevel item. if present, building is delegated
    ## to a docker container, otherwise the local machine is used to
    ## build.
    docker:

      ## Docker image that contains the Yocto requirements for building plus
      ## ronto tool (this tool) and optionally if desired the google repo tool.
      image: almedso/yocto-bitbaker:latest

      ## Privatized_image item indicates that a privatized image is to be used
      ## if it is present. If additionally an image name is given, this image
      ## name is used instead of the default.
      ## privatized images are needed if sources need to be pulled where access
      ## credentials (ssh key pairs) are required. Only in privatized build
      ## containers ssh key pairs and ssh configuration can be injected.
      ## privatized means: a user 'yocto' exists that has the same uid:gid like
      ## the invoking user. The users home directory is '/home/yocto'.
      ## Yocto builds cannot be executed as root.
      privatized_image: # my-yocto-bitbaker

      ## The docker container requires several volumes to be injected.
      ## Per volume mapping there is the directory name/volume name on
      ## the _host_ side and the directory name on the _container_ side.
      ## The respective names are arranged along those keys.

      ## A project root directory must be injected as volume to the container.
      ## On the host side the directory is always the project directory (as
      ## the name suggests. It cannot be configured differently.
      project_dir: /yocto/root

      ## The cache directory is the optional.
      ## If not given, all caching is done inside the container and thrown
      ## away when the container is destroyed.
      ## The site.conf script should set download cache (DL_DIR) and
      ## Shared state cache (SSTATE_DIR) to directories below this directory
      cache_dir:
        host: $(pwd)/../cache  ## one level up the project directory
        container: /yocto/cache  ## interacts with side.conf settings

      ## If a publishing dir is given publishing of results (images or packages)
      ## is possible. This means images or packages are copied/rsynced
      ## to the respective container path. and would show up on the host path.
      publish_dir:
        host: volume or path
        ## Used as default by this script
        container: /yocto/publish

Variables
---------

Definitions can be overwritten by environment variables.
There are two constraints:

* Each used environment variable must be listed in the default
  section.
* A default value must be given for every environment variable.
  In case a certain environment variable is not set, this default
  is used.

Assuming on the shell the SSTATE_DIR environment variable is set:

.. code :: console

    export SSTATE_DIR=/yocto/foobar

and the content of the *ronto.yml* is:

.. code :: yaml

    # Environment variable defaults
    defaults:
      DL_DIR: "/yocto/foo"
      SSTATE_DIR: "/yocto/bar"
    build:
      download: "{{ DL_DIR }}"
      shared_state: "{{ SSTATE_DIR }}"

*download* will be set to */yocto/foo* (the default) and
*shared_state* will be set to */yocto/foobar* (obtained from the process
environment.
