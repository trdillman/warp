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

run_precommit="${WARP_RUN_PRECOMMIT:-0}"
suite="${WARP_TEST_SUITE:-smoke}"

if [[ "$run_precommit" == "1" ]]; then
    echo "Running pre-commit checks..."
    uvx pre-commit run -a
fi

if [[ "$suite" == "all" ]]; then
    echo "Running full test suite..."
    uv run --extra dev -m warp.tests -s autodetect
else
    echo "Running smoke tests..."
    uv run --extra dev -m unittest warp.tests.test_utils
fi

echo "Maintenance completed successfully."
