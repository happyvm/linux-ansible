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
