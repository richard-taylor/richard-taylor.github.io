#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
pwd

# run the python unit tests

python3 -m unittest -v
