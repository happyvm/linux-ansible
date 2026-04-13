# ansible-linux-platform

Base de repository Ansible **production-ready** pour le patching Linux et le hardening multi-site.

## Capacités couvertes
- Patching RPM (RHEL/CentOS) avec logique **current / legacy / obsolete**.
- Patching Debian avec rings homogènes.
- Hardening CIS + overlays ANSSI/interne via profils compatibles.
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
- `roles/hardening_engine`: application profil + overlays.
- `roles/reporting`: rapport final consolidé.
- `docs/`: conventions d’architecture et modèle de données.

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
