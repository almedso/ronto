Feature: Repotool fetching

Scenario: fetch command from scratch only defaults
    Given a rontofile content as
        """
        repo:
          url: git@github.com:almedso/repo-yocto.git
        """
    Given empty sources
    When I finally enter "--dryrun --verbose fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Google manifest repository
        \* Init repo from git@github.com:almedso/repo-yocto.git
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo init -u git@github.com:almedso/repo-yocto.git -m default.xml -b master
        \* Sync repo
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo sync
        \* Docker decorator - done
        """


Scenario: fetch command from scratch with branch and manifest
    Given a rontofile content as
        """
        defaults:
          BRANCH: master
          MANIFEST: default.xml
        repo:
          url: git@github.com:almedso/repo-yocto.git
          branch: "{{ BRANCH }}"
          manifest: "{{ MANIFEST }}"
        """
    Given empty sources
    When I finally enter "--dryrun --verbose fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Google manifest repository
        \* Init repo from git@github.com:almedso/repo-yocto.git
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo init -u git@github.com:almedso/repo-yocto.git -m default.xml -b master
        \* Sync repo
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo sync
        \* Docker decorator - done
        """

Scenario: fetch command from scratch with branch and manifest overwrite
    Given a rontofile content as
        """
        defaults:
          BRANCH: master
          MANIFEST: default.xml
        repo:
          url: git@github.com:almedso/repo-yocto.git
          branch: "{{ BRANCH }}"
          manifest: "{{ MANIFEST }}"
        """
    Given empty sources
    When I finally enter "--dryrun --verbose --env BRANCH=foo --env MANIFEST=bar.xml fetch"
    Then ronto prints
        """
        \* CLI environment parameters: \['BRANCH=foo', 'MANIFEST=bar.xml'\]
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Google manifest repository
        \* Init repo from git@github.com:almedso/repo-yocto.git
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo init -u git@github.com:almedso/repo-yocto.git -m bar.xml -b foo
        \* Sync repo
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo sync
        \* Docker decorator - done
        """

Scenario: fetch command with enforced update
    Given a rontofile content as
        """
        repo:
          url: git@github.com:almedso/repo-yocto.git
        """
    Given empty sources
    When I finally enter "--dryrun --verbose fetch --force"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Google manifest repository
        \* Init repo from git@github.com:almedso/repo-yocto.git
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo init -u git@github.com:almedso/repo-yocto.git -m default.xml -b master
        \* Sync repo
        dry working dir: /home/volker/repos/yocto/ronto
        dry: repo sync
        \* Docker decorator - done
        """
