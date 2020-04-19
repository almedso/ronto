Feature: publish (batch mode only)

Scenario: no publish ok
    Given a rontofile content as
        """
        build:
        """
    When I finally enter "--dryrun --verbose publish --only-packages"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Docker decorator - done
        """

@clean
Scenario: only publish
    Given a rontofile content as
        """
        build:
          packageindex: true
        publish:
          webserver_host_dir: build/publish
        """
    Given "build/tmp-foo/deploy/ipk/my" exists
    When I finally enter "--dryrun --verbose publish --only-packages"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        dry working dir:
        dry: rsync -ah .*build/tmp-foo/deploy/ipk build/publish/feeds
        \* Docker decorator - done
        """

@clean
Scenario: no package source error
    Given a rontofile content as
        """
        build:
          packageindex: true
        publish:
          webserver_host_dir: build/publish
        """
    When I finally enter "--dryrun --verbose publish --only-packages"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        There is no .ipk. package directory
        """

@clean
Scenario: multiple package sources error
    Given a rontofile content as
        """
        build:
          packageindex: true
        publish:
          webserver_host_dir: build/publish
        """
    Given "build/tmp-foo/deploy/ipk/my" exists
    Given "build/tmp-bar/deploy/ipk/my" exists
    When I finally enter "--dryrun --verbose publish --only-packages"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        There are multiple distributions - do know which is relevant
        """

@clean
Scenario: single machine default image_type
    Given a rontofile content as
        """
        build:
          packageindex: true
        publish:
          webserver_host_dir: build/publish
        """
    Given "build/tmp-foo/deploy/ipk/my" exists
    Given "build/tmp-foo/deploy/images/quirin" exists
    When I finally enter "--dryrun --verbose publish --image ams-image-dev:quirin "
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        dry working dir:
        dry: rsync -ah .*build/tmp-foo/deploy/ipk build/publish/feeds
        \* Publish target ams-image-dev-quirin.wic
        dry working dir:
        dry: cp -fL .*build/tmp-foo/deploy/images/quirin/ams-image-dev-quirin.wic build/publish/images
        \* Docker decorator - done
        """

@clean
Scenario: single machine multiple image_type no packages
    Given a rontofile content as
        """
        publish:
          webserver_host_dir: build/publish
        """
    Given "build/tmp-foo/deploy/images/quirin" exists
    When I finally enter "--dryrun --verbose publish --image ams-image-dev:quirin -twic:tar.gz"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Publish target ams-image-dev-quirin.wic
        dry working dir:
        dry: cp -fL .*build/tmp-foo/deploy/images/quirin/ams-image-dev-quirin.wic build/publish/images
        \* Publish target ams-image-dev-quirin.tar.gz
        dry working dir:
        dry: cp -fL .*build/tmp-foo/deploy/images/quirin/ams-image-dev-quirin.tar.gz build/publish/images
        \* Docker decorator - done
        """

@clean
Scenario: no image output dir
    Given a rontofile content as
        """
        publish:
          webserver_host_dir: build/publish
        """
    When I finally enter "--dryrun --verbose publish --image ams-image-dev:quirin -twic:tar.gz"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        There is no image output directory
        """

@clean
Scenario: publish images multiple distros
    Given a rontofile content as
        """
        publish:
          webserver_host_dir: build/publish
        """
    Given "build/tmp-foo/deploy/images/quirin" exists
    Given "build/tmp-bar/deploy/images/quirin" exists
    When I finally enter "--dryrun --verbose publish --image ams-image-dev:quirin -twic:tar.gz"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        There are multiple distributions - do know which is relevant
        """

@clean
Scenario: images without publish flags are not published
    Given a rontofile content as
        """
        publish:
          webserver_host_dir: build/publish
        targets:
          - image: ams-image-dev
            machine: quirin
          - image: ams-image
            machine: quirin
        """
    Given "build/tmp-foo/deploy/images/quirin" exists
    When I finally enter "--dryrun --verbose publish"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Check for targets directly defined in 'ronto.yml'
        \* Verify target specifications
        \*   No verified target found -> use default target
        \* Docker decorator - done
        """
