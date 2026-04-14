from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "inventories" / "production" / "hosts.yml"


def _run_playbook(playbook: str, *, limit: str, extra_vars: dict[str, str]) -> None:
    if shutil.which("ansible-playbook") is None:
        import pytest

        pytest.skip("ansible-playbook is not available in environment")

    cmd = [
        "ansible-playbook",
        "-i",
        str(INVENTORY),
        str(ROOT / "playbooks" / playbook),
        "--check",
        "--limit",
        limit,
    ]

    for key, value in extra_vars.items():
        cmd.extend(["-e", f"{key}={value}"])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, (
        f"Playbook {playbook} failed with rc={result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_smoke_site_ring_rollout_minimal_execution():
    _run_playbook(
        "site_ring_rollout.yml",
        limit="rhel9-app-a1",
        extra_vars={
            "target_site": "site_a",
            "target_ring": "0",
            "ansible_connection": "local",
            "ansible_become": "false",
            "patching_enabled": "false",
            "hardening_enabled": "false",
        },
    )


def test_smoke_patching_only_minimal_execution():
    _run_playbook(
        "patching_only.yml",
        limit="rhel9-app-a1",
        extra_vars={
            "ansible_connection": "local",
            "ansible_become": "false",
            "patching_enabled": "false",
        },
    )


def test_smoke_hardening_only_minimal_execution():
    _run_playbook(
        "hardening_only.yml",
        limit="deb12-web-b1",
        extra_vars={
            "ansible_connection": "local",
            "ansible_become": "false",
            "hardening_enabled": "true",
            "patching_enabled": "false",
        },
    )
