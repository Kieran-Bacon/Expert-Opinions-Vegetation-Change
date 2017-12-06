#!/usr/bin/env bash

export PYTHONPATH=/root/code/

ls $PYTHONPATH

pytest -s /root/code/VegML/tests/TestAPIImplementations.py
