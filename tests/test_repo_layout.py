from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORED_TOP_LEVEL_ENTRIES = {".codex", ".git", ".runtime-cache", ".venv"}

ALLOWED_TOP_LEVEL_ENTRIES = {
    ".env.example",
    ".gitattributes",
    ".github",
    ".gitignore",
    ".python-version",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "README.md",
    "addon",
    "backends",
    "docs",
    "io",
    "presets",
    "pyproject.toml",
    "scripts",
    "sim_core",
    "tests",
    "uv.lock",
}

REQUIRED_TOP_LEVEL_ENTRIES = {
    ".github",
    "README.md",
    "addon",
    "backends",
    "docs",
    "io",
    "presets",
    "pyproject.toml",
    "scripts",
    "sim_core",
    "tests",
}

ALLOWED_WORKFLOW_FILES = {
    "blender-addon-release.yml",
}
class TestRepoLayout(unittest.TestCase):
    def test_top_level_entries_match_allowlist(self):
        top_level_entries = {
            path.name for path in REPO_ROOT.iterdir() if path.name not in IGNORED_TOP_LEVEL_ENTRIES
        }

        unexpected = sorted(top_level_entries - ALLOWED_TOP_LEVEL_ENTRIES)
        missing_required = sorted(REQUIRED_TOP_LEVEL_ENTRIES - top_level_entries)

        self.assertEqual(
            unexpected,
            [],
            msg=(
                "Unexpected top-level entries detected. "
                "If this is intentional, update ALLOWED_TOP_LEVEL_ENTRIES in tests/test_repo_layout.py."
            ),
        )
        self.assertEqual(
            missing_required,
            [],
            msg="Required top-level entries are missing. This indicates the addon repo layout drifted.",
        )

    def test_github_workflows_are_allowlisted(self):
        workflow_dir = REPO_ROOT / ".github" / "workflows"
        workflow_files = {path.name for path in workflow_dir.iterdir() if path.is_file()}

        unexpected = sorted(workflow_files - ALLOWED_WORKFLOW_FILES)
        missing = sorted(ALLOWED_WORKFLOW_FILES - workflow_files)

        self.assertEqual(
            unexpected,
            [],
            msg="Unexpected workflow files detected in .github/workflows.",
        )
        self.assertEqual(
            missing,
            [],
            msg="Expected addon release workflow is missing.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
