#!/usr/bin/env python
# coding=utf-8

"""MarkLogic Version Manager

Usage:
  mlvm list
  mlvm use <version>
  mlvm install <version> [--nightly]
  mlvm install --local <package>
  mlvm remove [<version> | --all]
  mlvm start
  mlvm stop
  mlvm init [<host>]
  mlvm eval <input> [--sjs | --xqy]
  mlvm ps
  
Options:
  -h --help     This screen
  --version     The version
  -n --nightly  Get a nightly instead of a GA release (requires credentials)
  -l --local    Install a package from a local file
  -a --all      Remove all versions
  --sjs         Evaluate Server-Side JavaScript
  --xqy         Evaluate XQuery

"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='2.0.0')
    print(arguments)
    
#   mlvm install <version> [--nightly]    Download and install
#   mlvm install --local <package>        Install from a local package
#   mlvm remove [<version> | --all]       Remove a version
#   mlvm stop                             Stop MarkLogic
#   mlvm start                            Start current version of MarkLogic 
#   mlvm status                           Display the current version
#   mlvm repair                           ?
#   mlvm init [<host>]                    Initialize a virgin installation
#   mlvm eval <input> [--sjs | --xqy]     Evaluate JavaScript or XQuery 
#   mlvm ps                               Process ids of MarkLogic