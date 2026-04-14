# Architecture cible

## 1) Séparation des responsabilités
- `context_resolver`: normalisation et validation du contexte hôte (mode `rollout` ou `standalone`).
- `patching_common`: orchestration patching OS.
- `patching_rpm`: cas RHEL/CentOS (modernes, legacy, obsolete + vault).
- `patching_debian`: cas Debian.
- `reboot_manager`: gestion reboot contrôlée avec fallback si `needs-restarting` est absent.
- `hardening_selector`: sélection profil compatible.
- `hardening_engine`: **placeholder structuré** (préchecks + plan CIS/overlays, remédiations à brancher).
- `reporting`: synthèse finale par hôte.

## 2) Rings
Mapping fixe depuis `environment_type`:
- dev -> 0
- test -> 1
- preprod -> 2
- prod_standard -> 3
- prod_critical -> 4

Le ring est résolu automatiquement via `environment_ring_map`.
- En `site_ring_rollout.yml`, `target_ring` est obligatoire et validé.
- En playbooks unitaires (`patching_only.yml`, `hardening_only.yml`), `target_ring` est optionnel (`context_resolver_mode=standalone`).

## 3) Defaults globaux attendus
Dans `inventories/production/group_vars/all/00-global.yml` :
- `patching_enabled: true`
- `hardening_enabled: true`
- `hardening_mode: auto`
- `hardening_profile_mode: auto`
- `os_support_tier: auto`
- `allow_obsolete_os: false`
- `allow_vault_repos: false`
- `risk_acknowledged: false`
- mappings centraux: `environment_ring_map`, `os_support_tiers`, `hardening_mode_policy`, `rollout_serial_by_ring`, `rollout_max_fail_percentage_by_ring`, `hardening_overlay_matrix`.

## 4) Support lifecycle
- `current`: patching complet + hardening audit/enforce.
- `legacy`: patching conditionnel + hardening prudent.
- `obsolete`: audit prioritaire, patch best-effort, warning explicite.

## 5) Garde-fous
- Refus si métadonnées minimales absentes.
- Refus si `environment_ring_map`/`os_support_tiers`/`hardening_mode_policy` incomplets.
- Refus si obsolete sans acceptation explicite du risque.
- Refus CentOS 6/7 sans `allow_vault_repos=true`.

## 6) Scalabilité 1500 applications
- Pas de rôle par application.
- Factorisation via profils + overlays + exceptions documentées dans `group_vars/` et `host_vars/`.
- Déploiement progressif piloté par `serial`/`max_fail_percentage`.
