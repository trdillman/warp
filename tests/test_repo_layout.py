from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Explicit allowlist for tracked top-level entries in this repository.
ALLOWED_TOP_LEVEL_ENTRIES = {
    ".clang-format",
    ".coderabbit.yml",
    ".env.example",
    ".gitattributes",
    ".github",
    ".gitignore",
    ".gitlab",
    ".gitlab-ci.yml",
    ".greptile",
    ".nspect-allowlist.toml",
    ".pre-commit-config.yaml",
    ".python-version",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "CLAUDE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "DECISIONS.md",
    "LICENSE.md",
    "NOTES.md",
    "PLAN.md",
    "PUBLICATIONS.md",
    "README.md",
    "SECURITY.md",
    "START_HERE.md",
    "TODO.md",
    "VERSION.md",
    "addon",
    "asv",
    "asv.conf.json",
    "backends",
    "build_docs.py",
    "build_lib.py",
    "build_llvm.py",
    "deps",
    "design",
    "docker",
    "docs",
    "io",
    "licenses",
    "notebooks",
    "presets",
    "pyproject.toml",
    "scripts",
    "setup.py",
    "sim_core",
    "tests",
    "tools",
    "uv.lock",
    "warp",
}

# Must-exist entries to prevent accidental layout drift or legacy reintroduction.
REQUIRED_TOP_LEVEL_ENTRIES = {
    "addon",
    "sim_core",
    "presets",
    "backends",
    "io",
    "scripts",
    "docs",
    "tests",
    ".github",
    "README.md",
    "pyproject.toml",
    "uv.lock",
}

ALLOWED_WORKFLOW_FILES = {
    "blender-addon-release.yml",
    "build-warp-builder-images.yml",
    "ci.yml",
    "codeql.yml",
    "draft-release.yml",
    "pr.yml",
    "sphinx.yml",
}


def _run_git(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


class TestRepoLayout(unittest.TestCase):
    def test_top_level_entries_match_allowlist(self):
        top_level_entries = set(_run_git("ls-tree", "--name-only", "HEAD"))

        unexpected = sorted(top_level_entries - ALLOWED_TOP_LEVEL_ENTRIES)
        missing_required = sorted(REQUIRED_TOP_LEVEL_ENTRIES - top_level_entries)

        self.assertEqual(
            unexpected,
            [],
            msg=(
                "Unexpected top-level entries detected. "
                "If this is intentional, update ALLOWED_TOP_LEVEL_ENTRIES in "
                "tests/test_repo_layout.py."
            ),
        )
        self.assertEqual(
            missing_required,
            [],
            msg=("Required top-level entries are missing. This may indicate a broken or legacy project layout."),
        )

    def test_github_workflows_are_allowlisted(self):
        workflow_paths = _run_git("ls-files", ".github/workflows")
        workflow_files = {Path(path).name for path in workflow_paths}

        unexpected = sorted(workflow_files - ALLOWED_WORKFLOW_FILES)
        missing = sorted(ALLOWED_WORKFLOW_FILES - workflow_files)

        self.assertEqual(
            unexpected,
            [],
            msg=(
                "Unexpected workflow files detected in .github/workflows. "
                "This guardrail prevents reintroduction of legacy workflows."
            ),
        )
        self.assertEqual(
            missing,
            [],
            msg="Expected allowlisted workflow files are missing.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
