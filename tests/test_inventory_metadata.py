from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOSTS_FILE = ROOT / "inventories" / "production" / "hosts.yml"
HOST_VARS_DIR = ROOT / "inventories" / "production" / "host_vars"
GLOBAL_DEFAULTS = ROOT / "inventories" / "production" / "group_vars" / "all" / "00-global.yml"
DATA_MODEL_DOC = ROOT / "docs" / "data-model.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _keys_in_yaml_text(content: str) -> set[str]:
    return set(re.findall(r"(?m)^([a-z_][a-z0-9_]*)\s*:", content))


def _scalar_value_in_yaml_text(content: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{key}:\s*([a-z0-9_]+)\s*$", content)
    return match.group(1) if match else None


def _groups_to_hosts(inventory: str, group_prefix: str) -> dict[str, set[str]]:
    groups: dict[str, set[str]] = {}
    group_block_pattern = re.compile(
        rf"(?ms)^(\s*)({group_prefix}[a-z0-9_]+):\n\1\s+hosts:\n((?:\1\s{{4}}[a-z0-9-]+:\n)+)"
    )
    host_pattern = re.compile(r"(?m)^\s*[a-z0-9-]+:\s*$")

    for match in group_block_pattern.finditer(inventory):
        group = match.group(2)
        host_lines = match.group(3)
        hosts = {
            host_line.strip().removesuffix(":")
            for host_line in host_pattern.findall(host_lines)
        }
        groups[group] = hosts

    return groups


def test_host_var_filenames_are_declared_in_inventory_hosts():
    inventory = _read(HOSTS_FILE)
    inventory_hosts = set(re.findall(r"(?m)^\s{12}([a-z0-9-]+):\s*$", inventory))

    host_var_hosts = {path.stem for path in HOST_VARS_DIR.glob("*.yml")}
    missing_from_inventory = sorted(host_var_hosts - inventory_hosts)

    assert not missing_from_inventory, (
        "Some host_vars files do not match a host declared in inventory: "
        f"{missing_from_inventory}"
    )


def test_host_vars_define_required_minimal_metadata_fields():
    required_fields = {
        "application_id",
        "application_family",
        "environment_type",
        "site",
        "resource_class",
        "os_family_normalized",
        "os_major",
    }

    missing_by_host = {}
    for path in sorted(HOST_VARS_DIR.glob("*.yml")):
        keys = _keys_in_yaml_text(_read(path))
        missing = sorted(required_fields - keys)
        if missing:
            missing_by_host[path.name] = missing

    assert not missing_by_host, f"Missing required metadata in host_vars: {missing_by_host}"


def test_documented_data_model_keys_exist_in_defaults_or_host_vars():
    documented_keys = set(re.findall(r"(?m)^-\s+([a-z_][a-z0-9_]*)\s*$", _read(DATA_MODEL_DOC)))
    assert documented_keys, "No documented keys found in docs/data-model.md"

    defaults_keys = _keys_in_yaml_text(_read(GLOBAL_DEFAULTS))
    host_var_union = set()
    for path in HOST_VARS_DIR.glob("*.yml"):
        host_var_union.update(_keys_in_yaml_text(_read(path)))

    defined_keys = defaults_keys | host_var_union
    missing = sorted(documented_keys - defined_keys)

    assert not missing, (
        "Keys documented in docs/data-model.md must be defined either in global defaults "
        f"or in host_vars files. Missing: {missing}"
    )


def test_host_vars_are_consistent_with_inventory_dimension_groups():
    inventory = _read(HOSTS_FILE)
    site_groups = _groups_to_hosts(inventory, "site_")
    environment_groups = _groups_to_hosts(inventory, "environment_type_")
    resource_groups = _groups_to_hosts(inventory, "resource_class_")

    mismatches = []
    for path in sorted(HOST_VARS_DIR.glob("*.yml")):
        host_name = path.stem
        content = _read(path)

        site = _scalar_value_in_yaml_text(content, "site")
        environment_type = _scalar_value_in_yaml_text(content, "environment_type")
        resource_class = _scalar_value_in_yaml_text(content, "resource_class")

        expected_groups = {
            f"site_{site}",
            f"environment_type_{environment_type}",
            f"resource_class_{resource_class}",
        }

        for expected_group in expected_groups:
            source_mapping = (
                site_groups
                if expected_group.startswith("site_")
                else environment_groups
                if expected_group.startswith("environment_type_")
                else resource_groups
            )

            if expected_group not in source_mapping:
                mismatches.append(f"{host_name}: missing group {expected_group} in inventory")
                continue
            if host_name not in source_mapping[expected_group]:
                mismatches.append(f"{host_name}: not found in {expected_group}")

    assert not mismatches, (
        "Host metadata must align with inventory dimension groups "
        f"(site/environment_type/resource_class). Problems: {mismatches}"
    )
