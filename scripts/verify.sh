#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=${VERIFY_ROOT:-$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)}
CXX_BIN=${CXX:-clang++}

exec python3 "$SCRIPT_DIR/verify_content.py" --root "$PROJECT_ROOT" --compiler "$CXX_BIN" "$@"
