#!/bin/sh

command -v indoc >/dev/null 2>&1 || { echo >&2 "Building the documentation requires the 'indoc' documentation generator to be installed (see https://www.npmjs.com/package/indoc)."; exit 1; }

echo "Building documentation..."

indoc -c indoc.json
#node ~/projects/native/indoc/bin/main.js -c indoc.json
