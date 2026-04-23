# AGENTS.md

OpenCode skills repository for Linux system troubleshooting and Proxmox VE cluster diagnostics.

## Repository Structure

- `linux-precision-triage/` - Ubuntu 24.04+ diagnostics (token-optimized)
- `pve-cluster-doctor/` - Proxmox VE cluster maintenance
- `pve-ufw-manager/` - UFW firewall automation for PVE
- `humanizer-zh-TW/` - Chinese (Traditional) response formatter
- `docusaurus-anchor-syntax/` - Docusaurus markdown helper
- `web-design-guidelines/` - Frontend design patterns
- `opencode-server/` - OpenCode server configuration

## Slash Commands

| Command | Skill | Description |
|---------|-------|-------------|
| `/linux-triage` | linux-precision-triage | System health snapshot |
| `/linux-net-audit` | linux-precision-triage | Network stack scan |
| `/linux-storage-audit` | linux-precision-triage | Storage pool diagnostics |
| `/linux-cluster-audit` | linux-precision-triage | Cluster quorum check |
| `/pve-vm-stuck` | pve-cluster-doctor | VM/LXC rescue |
| `/pve-health` | pve-cluster-doctor | Cluster health snapshot |
| `/pve-storage-audit` | pve-cluster-doctor | Storage backend diagnostics |
| `/pve-quorum-fix` | pve-cluster-doctor | Quorum emergency repair |
| `/pve-ufw-status` | pve-ufw-manager | Check firewall status |
| `/pve-ufw-apply` | pve-ufw-manager | Apply firewall rules |
| `/pve-ufw-dry-run` | pve-ufw-manager | Preview firewall changes |
| `/pve-ufw-rollback` | pve-ufw-manager | Rollback to previous rules |
| `/pve-ufw-logs` | pve-ufw-manager | View firewall logs |

## Critical Constraints

- **No build/test/lint**: This is a skill library, not a software project
- **Preserve YAML frontmatter**: Do not modify `name`, `description`, `commands` in `SKILL.md` files
- **Token efficiency**: Linux triage skills prioritize minimal-output commands (`-br`, `-n`, `--no-pager`, `grep` filters)
- **PVE tools**: Skills use `qm`, `pct`, `pvesm`, `pvecm`, `pveceph` CLI tools

## File Conventions

- Each skill has a `SKILL.md` entry point with YAML frontmatter
- Knowledge base files live in `knowledge/` subdirectories
- Scripts live in `scripts/` subdirectories

