# aggregate-port-options

<a href="https://repology.org/project/aggregate-port-options/versions">
        <img src="https://repology.org/badge/vertical-allrepos/aggregate-port-options.svg" alt="Packaging status" align="right">
</a>

![CI](https://github.com/AMDmi3/aggregate-port-options/workflows/CI/badge.svg)
[![PyPI downloads](https://img.shields.io/pypi/dm/aggregate-port-options.svg)](https://pypi.org/project/aggregate-port-options/)
[![Github commits (since latest release)](https://img.shields.io/github/commits-since/AMDmi3/aggregate-port-options/latest.svg)](https://github.com/AMDmi3/aggregate-port-options)

## Overview

This tool is intended for FreeBSD Ports users - it checks options
settings of installed packages and compares them to list of default
options set in ports, generating overview of how each otion is handled
in different packages - is it left in its default state, globally
enabled/disabled or tuned individually for each port.

The purpose is to get overview of your options setup in form of either
compact report or code suitable for `make.conf` inclusion. This allows
you to fine tune and generalize your options settings, preserve them
and share accross different machines. This is especially useful if you
want to switch from building packages on host to poudriere and want to
preserve your manual options setup.

## Usage

```
usage: aggregate-port-options [-h] [-d] [-v] [-p PORTS_PATH] [-m]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           enable debug logging (default: False)
  -v, --verbose         enable verbose output (default: 0)
  -p PORTS_PATH, --ports-path PORTS_PATH
                        path to ports tree (default: /usr/ports)
  -m, --make-conf       generate make.conf (default: False)
```

Use `-d` to show progress of operation (as it takes time to poll
ports for default options), `-v` to increase verbosity of generated
report (once to include lists of packages for each option, twice to
list all options including ones which have not been changed from 
their default state), `-m` to generate `make.conf` code instead of
textual report.

## Example
