#!/usr/bin/env bash
set -euo pipefail

ansible-inventory -i inventories/production/hosts.yml --graph
