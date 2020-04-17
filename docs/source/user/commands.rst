Ronto Commands
==============

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

.. code :: yaml

    ronto docker --help
    ronto docker ls  # list content of project folder
    ronto docker --interactive  # run interactive bash in container

As without docker it is possible to run an bitbake tasks interactively
within a sourced Yocto environment like

.. code :: yaml

    ronto build --interactive

This is the same as:

.. code :: yaml

    ronto docker --interactive 'ronto build -i'

For convenience it is possible to cleanup docker by:

* Remove the build container:

.. code :: yaml

    ronto docker --rm-container pwd  # pwd is just a short arbitrary command

* Remove the build container, the privatized image

.. code :: yaml

    ronto docker --rm-priv-image pwd

* Remove the build container, the privatized image and also the pulled big
  image that contains the yocto prerequisite tools.

.. code :: yaml

    ronto docker --rm-priv-image pwd
