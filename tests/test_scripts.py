from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]


def test_validate_inventory_script_is_executable_and_targets_prod_inventory():
    script = ROOT / "scripts" / "validate-inventory.sh"
    content = script.read_text(encoding="utf-8")

    assert content.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in content
    assert "ansible-inventory -i inventories/production/hosts.yml --graph" in content

    mode = script.stat().st_mode
    assert mode & os.X_OK, "scripts/validate-inventory.sh must be executable"
