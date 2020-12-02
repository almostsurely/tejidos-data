#!/bin/bash

mypy tejidos tests
pylint tejidos tests
python -m nose2