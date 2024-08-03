#!/bin/bash

# Check for python
if command -v python &> /dev/null
then
    PYTHON_CMD=python
elif command -v python3 &> /dev/null
then
    PYTHON_CMD=python3
elif command -v py &> /dev/null
then
    PYTHON_CMD=py
else
    echo "No suitable Python installation found."
    exit 1
fi

# Run the Python script
# shellcheck disable=SC2164
cd "$(dirname "$0")"
$PYTHON_CMD main.py