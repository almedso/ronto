Feature: Simplest Rontofile

Scenario: fetch command
    Given a rontofile content as
        """
        git:
        """
    When I enter "--dryrun init"
    Then ronto prints
        """
        dry working dir:.*sources/poky
        dry: git remote update
        dry working dir:
        dry: bash -c source sources/poky/oe-init-build-env build
        """
