from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from presets import list_preset_metadata  # noqa: E402


def main() -> None:
    for meta in list_preset_metadata():
        tags = ",".join(meta.tags)
        print(f"{meta.preset_id}\t{meta.display_name}\t{meta.category}\t{tags}")


if __name__ == "__main__":
    main()
