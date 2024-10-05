#!/bin/bash
export PATH=$PATH:$HOME/.local/bin
poetry install -q
poetry build-lambda -q
echo "{}"