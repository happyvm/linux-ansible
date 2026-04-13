.PHONY: test lint lint-yaml lint-ansible

test:
	pytest -q

lint: lint-yaml lint-ansible

lint-yaml:
	yamllint .

lint-ansible:
	ansible-lint playbooks/patching_only.yml playbooks/hardening_only.yml roles inventories/production/hosts.yml
