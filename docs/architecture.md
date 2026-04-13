# Architecture cible

## 1) Séparation des responsabilités
- `context_resolver`: normalisation et validation du contexte hôte.
- `patching_common`: orchestration patching OS.
- `patching_rpm`: cas RHEL/CentOS (modernes, legacy, obsolete + vault).
- `patching_debian`: cas Debian.
- `reboot_manager`: gestion reboot contrôlée.
- `hardening_selector`: sélection profil compatible.
- `hardening_engine`: CIS + overlays ANSSI/interne.
- `reporting`: synthèse finale par hôte.

## 2) Rings
Mapping fixe depuis `environment_type`:
- dev -> 0
- test -> 1
- preprod -> 2
- prod_standard -> 3
- prod_critical -> 4

Le ring n'est jamais défini manuellement au niveau host.

## 3) Support lifecycle
- `current`: patching complet + hardening audit/enforce.
- `legacy`: patching conditionnel + hardening prudent.
- `obsolete`: audit prioritaire, patch best-effort, warning explicite.

## 4) Garde-fous
- Refus si métadonnées minimales absentes.
- Refus si obsolete sans acceptation explicite du risque.
- Refus CentOS 6/7 sans `allow_vault_repos=true`.

## 5) Scalabilité 1500 applications
- Pas de rôle par application.
- Factorisation via profils + overlays + exceptions documentées dans `group_vars/` et `host_vars/`.
- Déploiement progressif piloté par `serial`/`max_fail_percentage`.
