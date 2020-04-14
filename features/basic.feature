Feature: Ronto basic stuff

Scenario: cli version
    Given ronto is installed
    When I enter "--version"
    Then ronto prints "0.1.2"
