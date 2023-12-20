#!/bin/sh
set -euo pipefail

# Custom script to run the Redocly CLI bundler, then work around https://github.com/Redocly/redocly-cli/issues/792
# Passes all CLI args to the Redocly CLI, then calls `sed` to make manual edits as needed
redocly $@ | \
    sed -e s_http-request.json_\'#/components/schemas/http-request\'_g
