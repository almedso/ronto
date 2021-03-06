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

Rontofile protocol version
..........................

Since the *ronto.yml* is subject to modification a strict mode reading
is supported if a version tag is set. The version is an unsigned integer.

.. code :: yaml

   ## providing a version forces ronto to check against the list of
   ## supported versions. If no version is given, ronto just tries
   ## its best.
   version: 1

In case version a version is set processing is stopped if

* either the version cannot be converted to an unsigned integer
* or the version is higher than the currently supported version.

This documentation references to *ronto.yml* protocol *version 1*.
This related **ronto** applications supports to *ronto.yml*
protocol *version 1*.

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

      ## <build_dir>/conf/site.conf is used to establish site specific settings
      ## Use an alternative file to establish <build_dir>/conf/site.conf
      ## Default is site.conf in project root directory
      site:
        file: site.conf ## path is relative to project root directory

Build Targets
.............

Build targets are best defined in the meta layer where machines and images
are defined. This is where they belong to.

.. code :: yaml

  ## Part of the build section
  build:
    ## Build targets are best defined by referencing a remote yaml formatted
    ## file containing a list of target specification.
    ## The file should be in the repository where respective machines/ images
    ## are defined and therefore are known.
    targets_file: sources/my-repo/conf/build-targets.yml

    ## If the targets_file item is not given, alternatively the targets are
    ## given by the targets items directly. The sub-element is a list of
    ## targets. If not given the yocto/poky getting started default is
    ## assumed.
    targets:
      - image: core-image-sato  ## yocto default
        machine: qemux86  ## of getting started


The *targets_file* yaml format is a list of dictionaries that must
have *machine* and *image* keys. Other keys are possible like
publish that indicates that further processing, like publishing
the build artifact.

.. code :: yaml

    - image: ams-image
      machine: roderigo
      publish: yes
    - image: ams-image
      machine: roderigo
      publish: no



Publishing
..........

Different targets are possible and useful.
Publishing happens to certain web URL's that are provided
by a web server. on the backend site those urls are mapped
to a publishing base directory.

* *image artifacts* are needed for initial installation.
* *package artifacts* are needed for individual package update
  via package management.

Furthermore, publishing of root filesystems via nfs as well
as and kernels and device trees via tftp boot protocol.
is usefully during development.


.. code :: yaml

    ## Publishing of packages and
    ## if set 'publish_package is defined packageing actions are performed
    publish:
      ## directory where packages will be sent to.
      ## must be an absolute path
      ## if in docker part of the publish volume
      ## if not set - and docker is configured this is equal
      ## to docker: -> publish_dir: -> container
      webserver_host_dir: xxx
      ## relative path extension to webserver_host_dir
      ## pointing to package feed root
      ## if set -> build output of packages packages are "rsynced" to that folder
      package_dir: feeds  ## default feeds
      ## relative path extension to webserver_host_dir
      ## pointing to image folder root
      ## if set targets with publish flag are copied over there
      image_dir: images  ## default images

.. note ::

    Package index has to be computed during build. If not configured by

    .. code :: yaml

        build:
          packageindex:

    publishing of packages will be suppressed.
  


.. _ronto-file-docker:

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

Definitions can be overwritten by shell environment variables or
variables injected on the command line via *-e* or *--env*
global option.

* Injection via command line parameter overwrites injection via
  environment variables.
* Injection via command line comes along with site effects but shows
  up in shell history
* Injection via shell environment variables might be important
  if secrets need to be passed on.
* Injection via shell environment might be complicated when used
  in a docker environment

There are two constraints:

* Each used environment variable must be listed in the default
  section.
* A default value must be given for every environment variable.
  In case a certain environment variable is not set, this default
  is used.

Variables without a default that are not provided
cause an processing error at runtime when they are evaluated.
Variables are evaluated at the moment they are needed (late evaluation).

It is possible to have up to two variable evaluation per yml element.

Assuming on the shell the SSTATE_DIR environment variable is set:

.. code :: console

    export SSTATE_DIR=/yocto/foobar

and the content of the *ronto.yml* is:

.. code :: yaml

    # Environment variable defaults
    defaults:
      DL_DIR: "/foo"
      YOCTO_BASE: "/yocto"
      SSTATE_DIR: "/yocto/bar"
    build:
      download: "{{ YOCTO_BASE }}{{ DL_DIR }}"
      shared_state: "{{ SSTATE_DIR }}"

*download* will be set to */yocto/foo* (the default) and
*shared_state* will be set to */yocto/foobar* (obtained from the process
environment.

Alternatively the SSTATE_DIR can be set on the command line like

.. code :: yaml

    SSTATE_DIR=/yocto/foobar ronto --env SSTATE_DIR=/yocto/foo init

The result would be that *shared_state* will be set to */yocto/foo*
(obtained from command line parameter (because of it's higher priority)).
