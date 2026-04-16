# AGENTS.md

This is an OpenCode skills repository containing diagnostic skills for Linux systems and Proxmox VE clusters.

## Structure
- `linux-precision-triage/` - Linux system troubleshooting skill (Ubuntu 24.04+)
- `pve-cluster-doctor/` - Proxmox VE cluster diagnostics skill

## What not to do
- Do not attempt to build, test, or lint this repo - it's a skill library, not a software project
- Do not modify skill YAML frontmatter (name, description, commands) without good reason

## Skills are invoked via slash commands
- `/linux-triage` - System health snapshot
- `/linux-net-audit` - Network stack scan
- `/linux-storage-audit` - Storage pool diagnostics
- `/linux-cluster-audit` - Cluster quorum check
- `/pve-vm-stuck` - VM/LXC rescue
- `/pve-health` - Cluster health snapshot
- `/pve-storage-audit` - Storage backend diagnostics
- `/pve-quorum-fix` - Quorum emergency repair