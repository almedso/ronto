Ronto Commands
==============

.. _command-bootstrap:

Bootstrap
.........

**ronto** simplifies the process of starting from scratch by bootstrapping
initial *ronto.yml* file and also a *site.conf* configuration.

This bootstrapping ends up in essential consistent settings.
**ronto** can manage different sources of configuration and recipes.

* do not manage at all - *ignore* option
* use a set of git repository specification - *git* option
* use repotool and manifest repository specification - *repo* option

Also, the build process runs

* either in a docker container
* or bare metal.

While bootstrapping those two orthogonal parameter ranges are considered.
Such that the set of user questions are minimized and tailored according to
those two parameters.

e.g. by invoking:

.. code :: console

   # get an idea
   ronto bootstrap --help
   # use manifest repository run in docker container
   ronto bootstrap --source repo --container
   # do not manage sources and do not run in a container
   ronto bootstrap -s ignore

.. _command-docker:

Docker
......

**ronto** offers the ability to run all Yocto build activities in a
docker container. This happens fully transparently if docker is
configured in the *ronto.yml*.

.. code :: yaml

    docker:

If the top level entry *docker* exists, all activities are performed
in a docker container.

There are many docker related things to configure in the *ronto.yml*
described at ronto-file-docker_.

As a prerequisite,

* docker engine and docker command must be installed and
* the user who runs *ronto* must have docker privileges.

Ronto deals with docker in the following way:

1. Ronto pulls a docker general Yocto tools  image
2. Ronto creates a privatized docker image for building.
3. Ronto creates a container with injected directories for
   project home, yocto cache and optionally, ssh keys and
   publishing
4. Ronto start the container and keep it running, exec into the
   container and run the required commands and tasks.
   After the work has been done stop the container.

The privatized image is derived from the general yocto image
and is characterized as follow:

* It has a default user named *yocto* including a home directory at the usual
  path */home/yocto* available. Most importantly, the UID and GId of the
  *yocto* user is the same as the calling user on the host. This is because
  yocto build jobs do not run as root (and must not). It allows to nicely
  inject ssh keys for pulling private source repositories while building,
  it allows reading, and housekeeping (removal) of produced build artifacts
  outside of the container if injected.
* It has the ronto tool installed. This allows invoking
  ronto commands inside the image as without docker, also fully transparently.

There a two ways to use build approaches with docker containers.

1. Build the the container on the fly from a capable image,
   mount in the build environment, build and remove the container.
2. Build a container (including mounting the build environment).
   Give the container a name and reuse the container. I.e.
   do not dispose the container.

Second approach is perceived as bad practice since additional
container housekeeping is required.

Still, due to the fact, that mounting the build environment might
require up to four volumes (complex). Since it is desireable to also
use the docker build easily without *ronto*, second approach has been
chosen.

Each yocto build environment has to have its own container, because
of different build environment mounts.

.. note ::

    The naming scheme for the container is simple and as follow:

    <privatized-docker-image-name>-<yocto project directory short name>.

    E.g. if the privatized docker image is *my-yocto-bitbaker*
    (This is the default if not differently specified in *ronto.yml*)
    and the yocto project directory is */home/volker/yocto/ams* the
    container name is: *my-yocto-bitbaker-ams*.

What volumes are mounted and where is fully described in the
ronto-file-docker_ section.

.. note ::

    Cache or download directories described e.g. in *site.conf*
    must address paths **inside** the container.

There is a dedicated *ronto docker* command that allows running
own command in the build container.

.. code :: console

    ronto docker --help
    ronto docker ls  # list content of project folder
    ronto docker --interactive  # run interactive bash in container

As without docker it is possible to run an bitbake tasks interactively
within a sourced Yocto environment like

.. code :: console

    ronto build --interactive

This is the same as:

.. code :: console

    ronto docker --interactive 'ronto build -i'

.. note ::

   Interactive session can be finished by typing *exit* command in bash.
   It might be possible that entering *exist* is required multiple times
   if docker exec bash calls e.g ronto command and ronto itself
   invokes a bash again for interactive building.

For convenience it is possible to cleanup docker by:

* Remove the build container:

.. code :: console

    ronto docker --rm-container pwd  # pwd is just a short arbitrary command

* Remove the build container, the privatized image

.. code :: console

    ronto docker --rm-priv-image pwd

* Remove the build container, the privatized image and also the pulled big
  image that contains the yocto prerequisite tools.

.. code :: console

    ronto docker --rm-priv-image pwd

.. _command-run:

Run Ronto Scripts
.................

like *npm* does, *ronto* offers a script execution with the *run* command.

.. code :: console

    $ ronto run

looks for the default script named *all* (borrowed from make) and runs that
script. if *all* is not defined in the *ronto.yml* file, it assumes the
following default for all.

.. code :: yaml

    scripts:
      all:
        - fetch
        - init --clean-conf
        - build

Thus, all will execute three steps by calling*ronto fetch*,
*ronto --clean-conf* and *build*  as sub-processes sequencially.

It will stop after an error and not continue any further steps.

Environment variables will be passed on. and so would global settings like
verbosity flag, dry-run flag or the set of command line variables.
injections.

It is possible to use environment variables or to set variables. The following
example shows how it works.

scripts do not have options. Any required variability can be easily addressed
by injecting command line variables prior the name of the run <script> command.

.. code :: console

    defaults:
      INTEGRATION: default
      RELEASE: stable
      MANIFEST: default
    repo:
      url: git@github.com:almedso/repo-yocto.git
      manifest: {{ MANIFEST }}.xml
    build: sources/ams/conf/{{ TARGET }}.yml
    scripts:
      release:
        - "--env MANIFEST={{ RELEASE }} fetch --force"
        - "init  --rm-build"
        - "--env TARGET={{ RELEASE }} build --publish"
      integration:
        - "--env MANIFEST={{ INTEGRATION }} fetch --force"
        - "init  --rm-conf"
        - "--env TARGET={{ INTEGRATION }} build --publish"

E.g the release script can be run like

.. code :: console

    $ ronto -env RELEASE=2020-04 run release

It runs release script and uses *2020-04* as *RELEASE* environment variable.
The variable is used to pick appropriate manifest files to pull the sources
and would select 2020-04 targets as being subject for a release.



