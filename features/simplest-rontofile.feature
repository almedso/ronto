Feature: Simplest Rontofile

@before.clean
Scenario: fetch command empty sources
    Given a rontofile content as
        """
        git:
        """
    When I finally enter "--dryrun fetch"
    Then ronto prints
        """
        dry working dir:.*sources
        dry: git clone
        """
