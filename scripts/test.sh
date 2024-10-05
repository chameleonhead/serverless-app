#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# cd ${SCRIPT_DIR}/../frontend && npm run test
cd ${SCRIPT_DIR}/../bff/auth && poetry run pytest --junitxml=unittests.xml --cov-report=xml:coverage.xml --cov=./auth
cd ${SCRIPT_DIR}/../api/hello && poetry run pytest --junitxml=unittests.xml --cov-report=xml:coverage.xml --cov=./hello
