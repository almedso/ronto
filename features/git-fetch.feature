Feature: Git fetching

@before.clean
Scenario: fetch command from scratch only defaults
    Given a rontofile content as
        """
        git:
        """
    When I finally enter "--dryrun --verbose fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Git repositories
        \* Clone git repo: git://git.yoctoproject.org/poky
        dry working dir: .*/sources
        dry: git clone git://git.yoctoproject.org/poky .*/sources/poky
        \* Docker decorator - done
        """

@before.clean
Scenario: fetch command from scratch two repos
    Given a rontofile content as
        """
        git:
          - git_url: git://git.yoctoproject.org/poky
            source_dir: sources/poky
          - git_url: git@github.com:almedso/repo-yocto.git
            source_dir: sources/ams
        """
    When I finally enter "--dryrun --verbose fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Git repositories
        \* Configured git repo: git://git.yoctoproject.org/poky
        \* Configured git repo: git@github.com:almedso/repo-yocto.git
        \* Clone git repo: git://git.yoctoproject.org/poky
        dry working dir: .*/sources
        dry: git clone git://git.yoctoproject.org/poky .*/sources/poky
        \* Clone git repo: git@github.com:almedso/repo-yocto.git
        dry working dir: .*/sources
        dry: git clone git@github.com:almedso/repo-yocto.git .*/sources/ams
        \* Docker decorator - done
        """

@slow
@before.clean
Scenario: fetch command with update
    Given a rontofile content as
        """
        git:
          - git_url: git@github.com:almedso/repo-yocto.git
            source_dir: sources/ams
        """
    When I enter "fetch"
    Then "sources/ams" contains a git repository
    When I finally enter "--dryrun --verbose fetch"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Git repositories
        \* Configured git repo: git@github.com:almedso/repo-yocto.git
        \* Update git repo: git@github.com:almedso/repo-yocto.git
        dry working dir: .*/sources/ams
        dry: git remote update
        \* Docker decorator - done
        """

@before.clean
Scenario: fetch command with enforced update
    Given a rontofile content as
        """
        git:
          - git_url: git@github.com:almedso/repo-yocto.git
            source_dir: sources/ams
        """
    When I enter "fetch"
    Then "sources/ams" contains a git repository
    When I finally enter "--dryrun --verbose fetch --force"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator
        \* Docker context not configured
        \* Do not run on docker
        \* Process fetch command
        \* Config base: Git repositories
        \* Configured git repo: git@github.com:almedso/repo-yocto.git
        \* Remove old sources - i.e. forced update
        \* Clone git repo: git@github.com:almedso/repo-yocto.git
        dry working dir: .*/sources
        dry: git clone git@github.com:almedso/repo-yocto.git .*sources/ams
        \* Docker decorator - done
        """
