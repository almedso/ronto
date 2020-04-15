Feature: Site.conf init for bitbake

@clean
Scenario: no site.conf
    Given a rontofile content as
        """
        build:
          site:
            file: 'foo.bar'
        """
    When I finally enter "--dryrun --verbose init"
    Then "{build/conf/site.conf}" does not exist
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

        \* Use site configuration file: foo.bar
        \* Docker decorator - done
        """

@clean
Scenario: site.conf is injected
    Given a rontofile content as
        """
        build:
          site:
        """
    Given "site.conf" exists
    When I finally enter "--verbose init"
    Then "build/conf/site.conf" does exist
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Run init: source sources/poky/oe-init-build-env build
        \* Use site configuration file: site.conf
        \* Create site.conf from: /home/volker/repos/yocto/ronto/site.conf
        \* Docker decorator - done
        """

@clean
Scenario: site.conf is injected from other file
    Given a rontofile content as
        """
        build:
          site:
            file: sources/site-conf
        """
    Given "sources/site-conf" exists
    When I finally enter "--verbose init"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Run init: source sources/poky/oe-init-build-env build
        \* Use site configuration file: sources/site-conf
        \* Create site.conf from: /home/volker/repos/yocto/ronto/sources/site-conf
        \* Docker decorator - done
        """
    Then "build/conf/site.conf" does exist

@clean
Scenario: site.conf is not overwritten
    Given a rontofile content as
        """
        build:
        """
    Given "site.conf" exists
        """
        new-content
        """
    Given "build/conf/site.conf" exists
        """
        old-content
        """
    When I finally enter "--verbose init"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process init command
        \* Run init: source sources/poky/oe-init-build-env build
        \* Use site configuration file: site.conf
        \* Docker decorator - done
        """
    Then "build/conf/site.conf" does exist containing "old-content"
