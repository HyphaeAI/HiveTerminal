#!/bin/bash
# Quick launcher for HiveTerminal with Python 3.13

source .venv-3.13/bin/activate
python -m hiveterminal.cli.entrypoint "$@"
