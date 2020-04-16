Feature: Ronto basic stuff

Scenario: cli version
    Given ronto is installed
    When I enter "--version"
    Then ronto prints "0.1.2"

Scenario: cli version
    Given a rontofile content as
        """
        version: 2
        """
    When I finally enter "--dryrun --verbose fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Check rontofile version
        Unsupported version of ronto.yml file
        """
    Then the exit code indicates an error
