#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export SA_FRONTEND_URL=$(cd ${SCRIPT_DIR}/../terraform && terraform output frontend_domain_name | tr -d '"')
cd ${SCRIPT_DIR}/../gauge && TAIKO_BROWSER_ARGS=--no-sandbox,--start-maximized,--disable-dev-shm-usage npm run test
