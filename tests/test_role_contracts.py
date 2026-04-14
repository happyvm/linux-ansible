from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ROLES_DIR = ROOT / "roles"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_all_roles_have_main_task_file():
    roles = [p for p in ROLES_DIR.iterdir() if p.is_dir()]
    missing = [role.name for role in roles if not (role / "tasks" / "main.yml").exists()]
    assert not missing, f"Roles missing tasks/main.yml: {missing}"


def test_all_roles_have_main_defaults_file():
    roles = [p for p in ROLES_DIR.iterdir() if p.is_dir()]
    missing = [role.name for role in roles if not (role / "defaults" / "main.yml").exists()]
    assert not missing, f"Roles missing defaults/main.yml: {missing}"


def test_include_role_targets_exist_as_local_roles():
    include_pattern = re.compile(
        r"(?ms)^\s*-\s+name:\s+.*?\n\s+ansible\.builtin\.include_role:\n\s+name:\s+([a-z_][a-z0-9_]*)\s*$"
    )

    referenced_roles = set()
    for task_file in ROLES_DIR.glob("*/tasks/main.yml"):
        referenced_roles.update(include_pattern.findall(_read(task_file)))

    existing_roles = {p.name for p in ROLES_DIR.iterdir() if p.is_dir()}
    missing = sorted(referenced_roles - existing_roles)
    assert not missing, f"include_role references unknown roles: {missing}"


def test_context_resolver_contains_core_guardrails():
    content = _read(ROLES_DIR / "context_resolver" / "tasks" / "main.yml")

    required_tokens = [
        "required_host_metadata",
        "environment_ring_map",
        "resolved_os_support_tier",
        "allow_obsolete_os | bool",
        "risk_acknowledged | bool",
        "resolved_hardening_mode",
        "resolved_risk_level",
    ]
    missing = [token for token in required_tokens if token not in content]
    assert not missing, f"context_resolver missing expected logic tokens: {missing}"


def test_patching_common_dispatches_by_os_family_and_reboot_toggle():
    content = _read(ROLES_DIR / "patching_common" / "tasks" / "main.yml")

    assert "name: patching_rpm" in content
    assert "name: patching_debian" in content
    assert "name: reboot_manager" in content
    assert "os_family_normalized in ['redhat', 'centos', 'rocky', 'almalinux']" in content
    assert "os_family_normalized in ['debian', 'ubuntu']" in content
    assert "when: patching_reboot_enabled | bool" in content


def test_patching_rpm_covers_current_legacy_and_obsolete_paths():
    content = _read(ROLES_DIR / "patching_rpm" / "tasks" / "main.yml")

    required_tokens = [
        "allow_vault_repos | bool",
        "ansible.builtin.dnf",
        "ansible.builtin.yum",
        "resolved_os_support_tier == 'current'",
        "resolved_os_support_tier == 'legacy'",
        "resolved_os_support_tier in ['legacy', 'obsolete']",
        "rpm_best_effort_on_obsolete | bool",
    ]

    missing = [token for token in required_tokens if token not in content]
    assert not missing, f"patching_rpm missing expected support-tier branches: {missing}"


def test_hardening_selector_and_engine_contract_is_consistent():
    selector_tasks = _read(ROLES_DIR / "hardening_selector" / "tasks" / "main.yml")
    selector_defaults = _read(ROLES_DIR / "hardening_selector" / "defaults" / "main.yml")
    engine_tasks = _read(ROLES_DIR / "hardening_engine" / "tasks" / "main.yml")
    global_defaults = _read(ROOT / "inventories" / "production" / "group_vars" / "all" / "00-global.yml")

    assert "name: hardening_engine" in selector_tasks
    assert "hardening_profile_mode != 'auto'" in selector_tasks
    assert ".get(os_family_normalized, {}).get(os_major, 'minimal')" in selector_tasks

    for os_family in ["redhat", "centos", "debian"]:
        assert f"{os_family}:" in selector_defaults

    assert "resolved_overlays" in engine_tasks
    assert "hardening_overlay_matrix" in engine_tasks
    assert "hardening_overlay_matrix:" in global_defaults


def test_reporting_role_contains_expected_payload_fields_and_persistence():
    content = _read(ROLES_DIR / "reporting" / "tasks" / "main.yml")

    required_report_keys = [
        "application_id",
        "application_family",
        "site",
        "environment_type",
        "ring",
        "support_tier",
        "hardening_mode",
        "hardening_profile",
        "risk_level",
        "warnings",
    ]

    for key in required_report_keys:
        assert re.search(rf"(?m)^\s{{6}}{key}:\s", content), f"Missing report key: {key}"

    assert "content: \"{{ host_report | to_nice_json }}\"" in content
    assert "delegate_to: localhost" in content
