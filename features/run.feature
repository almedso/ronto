Feature: Run command (dryrun only)

Scenario: 'default script all'
    Given a rontofile content as
        """
        scripts:
        """
    When I finally enter "--dryrun --verbose run"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Run script 'all'
        \* Run step ronto --file .* --verbose --dryrun fetch --force
        dry: ronto --file .* --verbose --dryrun fetch --force
        \* Run step ronto --file .* --verbose --dryrun init --rebuild-conf
        dry: ronto --file .* --verbose --dryrun init --rebuild-conf
        \* Run step ronto --file .* --verbose --dryrun build
        dry: ronto --file .* --verbose --dryrun build
        \* Script 'all' successfully finished
        """

Scenario: 'default script with two injected vars'
    Given a rontofile content as
        """
        scripts:
        """
    When I finally enter "--dryrun --env FOO=foo -eBAR=bar run"
    Then ronto prints
        """
        dry: ronto --file .* --dryrun --env FOO=foo --env BAR=bar fetch --force
        dry: ronto --file .* --dryrun --env FOO=foo --env BAR=bar init --rebuild-conf
        dry: ronto --file .* --dryrun --env FOO=foo --env BAR=bar build
        """

Scenario: 'script not found'
    Given a rontofile content as
        """
        scripts:
        """
    When I finally enter "--dryrun --verbose run not_found"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Run script 'not_found'
        Script 'not_found' not found
        """

Scenario: 'run script with vars'
    Given a rontofile content as
        """
        scripts:
          myscript:
            - fetch
            - build --targets {{ MYTARGET }}
        """
    When I finally enter "--dryrun -e MYTARGET=foo run myscript"
    Then ronto prints
        """
        dry: ronto --file .* --dryrun --env MYTARGET=foo fetch
        dry: ronto --file .* --dryrun --env MYTARGET=foo build --targets foo
        """"