Feature: Init for bitbake

@clean
Scenario: init from default
    Given a rontofile content as
        """
        git:
        """
    When I finally enter "--dryrun --verbose init"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Run init: source sources/poky/oe-init-build-env build
        dry working dir: /home/volker/repos/yocto/ronto
        dry: bash -c source sources/poky/oe-init-build-env build

        \* Use site configuration file
        \* Docker decorator - done
        """

@clean
Scenario: init from default with fetch option
    Given a rontofile content as
        """
        git:
        """
    When I finally enter "--dryrun --verbose init --fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Git repositories
        \* Clone git repo: git://git.yoctoproject.org/poky
        dry working dir: .*/sources
        dry: git clone git://git.yoctoproject.org/poky .*/sources/poky
        \* Docker decorator - done
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Run init: source sources/poky/oe-init-build-env build
        dry working dir: /home/volker/repos/yocto/ronto
        dry: bash -c source sources/poky/oe-init-build-env build

        \* Use site configuration file
        \* Docker decorator - done
        """

@clean
Scenario: init from with removal of local.conf and bblayer.conf
    Given a rontofile content as
        """
        git:
        """
    Given "build/conf/local.conf" exists
    Given "build/conf/bblayers.conf" exists
    When I finally enter "--dryrun --verbose init --rebuild-conf"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Remove local.conf and bblayers.conf in.*build/conf
        \* Run init: source sources/poky/oe-init-build-env build
        dry working dir: /home/volker/repos/yocto/ronto
        dry: bash -c source sources/poky/oe-init-build-env build

        \* Use site configuration file
        \* Docker decorator - done
        """
    Then "build/conf/local.conf" does not exist
    Then "build/conf/bblayers.conf" does not exist

@clean
Scenario: init from with removal of build directory
    Given a rontofile content as
        """
        git:
        """
    Given "build/conf/local.conf" exists
    Given "build/conf/bblayers.conf" exists
    When I finally enter "--dryrun --verbose init --clean-build"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Remove build directory \(cleanup\) build
        \* Run init: source sources/poky/oe-init-build-env build
        dry working dir: /home/volker/repos/yocto/ronto
        dry: bash -c source sources/poky/oe-init-build-env build

        \* Use site configuration file
        \* Docker decorator - done
        """
    Then "build/conf" does not exist
    Then "build" does not exist

@clean
Scenario: init from with removal of config directory
    Given a rontofile content as
        """
        git:
        """
    Given "build/conf/local.conf" exists
    Given "build/conf/bblayers.conf" exists
    When I finally enter "--dryrun --verbose init --clean-conf"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Remove configuration directory \(cleanup\) build/conf
        \* Run init: source sources/poky/oe-init-build-env build
        dry working dir: /home/volker/repos/yocto/ronto
        dry: bash -c source sources/poky/oe-init-build-env build

        \* Use site configuration file
        \* Docker decorator - done
        """
    Then "build/conf" does not exist
    Then "build" does exist
