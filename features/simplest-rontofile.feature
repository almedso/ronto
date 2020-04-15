Feature: Simplest Rontofile

Scenario: fetch command empty sources
    Given a rontofile content as
        """
        git:
        """
    Given empty sources
    When I finally enter "--dryrun fetch"
    Then ronto prints
        """
        dry working dir:.*sources
        dry: git clone
        """
