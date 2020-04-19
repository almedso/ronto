Feature: build command (batch mode only)

@before.clean
Scenario: no targets defined
    Given a rontofile content as
        """
        build:
        """
    When I finally enter "--dryrun --verbose build"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process build command
        \* Target Builder
        \* Builder init sourcing: source sources/poky/oe-init-build-env build
        \* Check for targets directly defined in 'ronto.yml'
        \* Verify target specifications
        \*   No verified target found -> use default target
        \* Start Bash session: Pid
        dry - Run build command: source sources/poky/oe-init-build-env build
        \**
        \* Build core-image-sato for qemux86
        \**
        dry - Run build command: MACHINE=qemux86 bitbake core-image-sato
        \* Do package index
        dry - Run build command: bitbake package-index
        dry - Run build command: exit
        \* Stop bash session: Pid
        \* Docker decorator - done
        """

@before.clean
Scenario: in ronto.yml two targets and no package-index defined
    Given a rontofile content as
        """
        build:
          packageindex: False
          targets:
            - image: bar-1
              machine: foo-1
            - image: bar-2
              machine: foo-2
        """
    When I finally enter "--dryrun --verbose build"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process build command
        \* Target Builder
        \* Builder init sourcing: source sources/poky/oe-init-build-env build
        \* Check for targets directly defined in 'ronto.yml'
        \* Verify target specifications
        \* Start Bash session: Pid
        dry - Run build command: source sources/poky/oe-init-build-env build
        \**
        \* Build bar-1 for foo-1
        \**
        dry - Run build command: MACHINE=foo-1 bitbake bar-1
        \**
        \* Build bar-2 for foo-2
        \**
        dry - Run build command: MACHINE=foo-2 bitbake bar-2
        dry - Run build command: exit
        \* Stop bash session: Pid
        \* Docker decorator - done
        """

@after.clean
Scenario: targets defined per file reference
    Given "sources/my-targets.yml" exists
        """
        - image: bar-1
          machine: foo-1
        - image: bar-2
          machine: foo-2
        """
    Given a rontofile content as
        """
        defaults:
          DIR: sources
          FILE: my-targets.yml
        build:
          packageindex: true
          targets_file: "{{DIR}}/{{FILE}}"
        """
    When I finally enter "--dryrun --verbose build"
    Then ronto prints
        """
        \* Read ronto.yml
        \* Update default variables
        \* Docker decorator - started
        \* Docker context not configured
        \* Do not run on docker
        \* Process build command
        \* Target Builder
        \* Builder init sourcing: source sources/poky/oe-init-build-env build
        \* Read targets from file: sources/my-targets.yml
        \* Verify target specifications
        \* Start Bash session: Pid
        dry - Run build command: source sources/poky/oe-init-build-env build
        \**
        \* Build bar-1 for foo-1
        \**
        dry - Run build command: MACHINE=foo-1 bitbake bar-1
        \**
        \* Build bar-2 for foo-2
        \**
        dry - Run build command: MACHINE=foo-2 bitbake bar-2
        \* Do package index
        dry - Run build command: bitbake package-index
        dry - Run build command: exit
        \* Stop bash session: Pid
        \* Docker decorator - done
        """
