from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PLAYBOOKS = [
    ROOT / "playbooks" / "site_ring_rollout.yml",
    ROOT / "playbooks" / "patching_only.yml",
    ROOT / "playbooks" / "hardening_only.yml",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_repository_has_expected_entrypoints():
    expected = [
        ROOT / "README.md",
        ROOT / "ansible.cfg",
        ROOT / "inventories" / "production" / "hosts.yml",
        ROOT / "scripts" / "validate-inventory.sh",
    ]
    missing = [str(p.relative_to(ROOT)) for p in expected if not p.exists()]
    assert not missing, f"Missing expected files: {missing}"


def test_playbooks_define_required_top_level_keys():
    required_patterns = [
        r"(?m)^-\s+name:\s+",
        r"(?m)^\s+hosts:\s+",
        r"(?m)^\s+gather_facts:\s+",
        r"(?m)^\s+roles:\s*$",
    ]

    for playbook in PLAYBOOKS:
        content = _read(playbook)
        for pattern in required_patterns:
            assert re.search(pattern, content), (
                f"{playbook.relative_to(ROOT)} missing required pattern: {pattern}"
            )


def test_roles_referenced_in_playbooks_are_documented_in_architecture():
    architecture = _read(ROOT / "docs" / "architecture.md")
    documented_roles = set(re.findall(r"`([a-z_]+)`", architecture))

    role_pattern = re.compile(r"(?m)^\s*-\s+role:\s*([a-z_][a-z0-9_]*)\s*$")

    for playbook in PLAYBOOKS:
        content = _read(playbook)
        referenced_roles = role_pattern.findall(content)
        assert referenced_roles, f"No roles found in {playbook.relative_to(ROOT)}"

        undocumented = sorted(set(referenced_roles) - documented_roles)
        assert not undocumented, (
            f"Roles in {playbook.relative_to(ROOT)} not present in docs/architecture.md: {undocumented}"
        )


def test_inventory_contains_site_and_environment_grouping():
    inventory = _read(ROOT / "inventories" / "production" / "hosts.yml")

    required_tokens = [
        "all:",
        "sites:",
        "environment_type_dev:",
        "environment_type_prod_standard:",
        "environment_type_prod_critical:",
        "resource_class_app:",
        "resource_class_db:",
        "resource_class_web:",
    ]

    missing = [token for token in required_tokens if token not in inventory]
    assert not missing, f"Inventory is missing expected sections: {missing}"
