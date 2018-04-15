#!/usr/bin/env bash

export PYTHONPATH=/root/code/

ls $PYTHONPATH

pylint /root/code/ExpertRep/*/*.py --max-line-length=120
pytest -s /root/code/ExpertRep/tests/*
find $PYTHONPATH -type f -name "*.py" | xargs python3 -m doctest -v
