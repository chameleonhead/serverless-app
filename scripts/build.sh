#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# cd ${SCRIPT_DIR}/../frontend && npm run test
cd ${SCRIPT_DIR}/../frontend && npm run build
cd ${SCRIPT_DIR}/../bff/auth && poetry build-lambda
cd ${SCRIPT_DIR}/../api/hello && poetry build-lambda
