# ansible-linux-platform

Base de repository Ansible pour le patching Linux et le hardening multi-site.

## Capacités couvertes
- Patching RPM (RHEL/CentOS) avec logique **current / legacy / obsolete**.
- Patching Debian avec rings homogènes.
- Sélection de profils de hardening CIS + overlays ANSSI/interne (moteur d'application en cours d'implémentation).
- Résolution de contexte automatique (site, environnement, ring, tier OS, risque).
- Déploiement progressif (site puis ring), garde-fous forts, reporting final par host.

## Structure
- `inventories/production/`: inventaire multi-site + variables factorisées.
- `playbooks/site_ring_rollout.yml`: orchestration principale site/ring.
- `roles/context_resolver`: validation métadonnées + calcul contexte.
- `roles/patching_common`: dispatch patching RPM/Debian + reboot.
- `roles/patching_rpm`: logique spécifique RHEL/CentOS legacy/obsolete incluse.
- `roles/patching_debian`: logique Debian.
- `roles/hardening_selector`: sélection profil/mode hardening.
- `roles/hardening_engine`: squelette du moteur d'application profil + overlays (placeholder actuel).
- `roles/reporting`: rapport final consolidé.
- `docs/`: conventions d’architecture et modèle de données.

## Qualité & vérifications
```bash
python -m pip install -r requirements-dev.txt
make lint   # yamllint + ansible-lint
make test   # tests structurels (pytest)
```

> Note: `make lint` couvre les rôles et les playbooks unitaires (`patching_only`, `hardening_only`).

## CI GitHub Actions
- Pipeline `CI` exécutée sur `push` (branche `main`) et `pull_request`.
- Jobs séparés: `lint` (`make lint`) et `tests` (`make test`).

## Exécution type
```bash
ansible-playbook -i inventories/production/hosts.yml playbooks/site_ring_rollout.yml \
  -e target_site=site_a -e target_ring=3
```

## Contrôles importants
- `fail` si métadonnées minimales absentes.
- `fail` si OS obsolete sans `risk_acknowledged=true`.
- `fail` si CentOS 6/7 sans `allow_vault_repos=true` quand vault requis.
- Hardening enforce désactivable automatiquement pour legacy/obsolete selon politique.

## Statut actuel du hardening
- Le rôle `hardening_engine` est actuellement un **placeholder** (bannières + calcul d'overlays), sans remédiations système effectives.
- Le dépôt fournit la structure, le routing et les garde-fous; les tâches de conformité doivent encore être branchées dans ce moteur.
