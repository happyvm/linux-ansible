# Modèle de données attendu

Variables de référence par host/groupe:
- application_id
- application_family
- environment_type
- site
- resource_class
- os_family_normalized
- os_major
- patching_enabled
- hardening_enabled
- hardening_mode
- allow_obsolete_os
- allow_vault_repos
- os_support_tier
- risk_acknowledged
- hardening_profile_mode

Exemple minimal dans `inventories/production/host_vars/`.
