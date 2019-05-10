#!/bin/bash
cd "$(dirname "$0")"

# Create virtual environment
python3.6 -m venv venv
if [ $? -ne 0 ]
then
    exit $?
fi

# Upgrade PIP
venv/bin/pip install --upgrade pip
if [ $? -ne 0 ]
then
    exit $?
fi

# Install requirements
venv/bin/pip install -r src/requirements.txt