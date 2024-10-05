#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${SCRIPT_DIR}/../frontend && npm run check-format
cd ${SCRIPT_DIR}/../frontend && npm run lint
cd ${SCRIPT_DIR}/../bff/auth && poetry run black --check .
cd ${SCRIPT_DIR}/../bff/auth && poetry run isort --check .
cd ${SCRIPT_DIR}/../bff/auth && poetry run flake8
cd ${SCRIPT_DIR}/../bff/auth && poetry run mypy .
cd ${SCRIPT_DIR}/../api/hello && poetry run black --check .
cd ${SCRIPT_DIR}/../api/hello && poetry run isort --check .
cd ${SCRIPT_DIR}/../api/hello && poetry run flake8
cd ${SCRIPT_DIR}/../api/hello && poetry run mypy .
