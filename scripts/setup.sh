#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -f .env ]]; then
    # shellcheck disable=SC1091
    source .env
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv is not installed or not on PATH."
    exit 1
fi

build_mode="${WARP_BUILD_MODE:-quick}"
needs_build=0

if [[ ! -f warp/bin/warp.so ]] || [[ ! -f warp/bin/warp-clang.so ]]; then
    needs_build=1
fi

if [[ "$needs_build" -eq 1 ]]; then
    echo "Warp native libraries missing, building (${build_mode})..."
    if [[ "$build_mode" == "full" ]]; then
        uv run build_lib.py
    else
        uv run build_lib.py --quick
    fi
else
    echo "Warp native libraries already present; skipping build."
fi

suite="${WARP_TEST_SUITE:-smoke}"
if [[ "$suite" == "all" ]]; then
    echo "Running full test suite..."
    uv run --extra dev -m warp.tests -s autodetect
else
    echo "Running smoke tests..."
    uv run --extra dev -m unittest warp.tests.test_utils
fi

echo "Setup completed successfully."
