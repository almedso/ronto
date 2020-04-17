Feature: docker command (dryrun only)

Scenario:
    Given a rontofile content as
        """
        build:
        """
    When I finally enter "--dryrun --verbose docker ls"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker context not configured
        \* No docker environment
        """

Scenario:
    Given a rontofile content as
        """
          docker:
        """
    When I finally enter "--dryrun --verbose docker --interactive"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker configuration found
        \* Docker context configured
        dry: Build or get privatized docker image: my-yocto-bitbaker
        \* Container already exists, reusing ...
        dry: Start container: my-yocto-bitbaker-
        \* Docker host - run interactive command 'bash'
        dry: \(interactive-in-container\) bash
        \* Docker host - command 'bash' finished
        dry: Stop container: my-yocto-bitbaker-
        """

