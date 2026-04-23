---
name: opencode-server
description: |
  Manage OpenCode server environment at /root/opencode-env/. 
  Use this skill when the user mentions: starting/stopping OpenCode server, 
  port 4096, secure_opencode.sh, firewall rules for opencode, iptables for 4096, 
  or any operations related to /root/opencode-env/ directory.
  Always use workdir: "/root/opencode-env" for all shell commands.
  Trigger on: "opencode serve", "啟動 server", "4096", "secure_opencode", 
  "iptables 4096", "防火牆", "firewall opencode", or directory operations in /root/opencode-env.
---

# OpenCode Server Skill

Instructions for managing the OpenCode server environment.

## Environment Location

- **Base Directory**: `/root/opencode-env/`
- **Key Files**:
  - `.env` - Contains `OPENCODE_SERVER_PASSWORD` and `ALLOWED_IPS`
  - `secure_opencode.sh` - Firewall setup + server launcher script
- **Port**: 4096
- **Required Hostname**: `--hostname 0.0.0.0` (must be explicit for external access)

## Critical Rules

1. **Always use workdir**: Every shell command MUST use `"workdir": "/root/opencode-env"`
2. **Port 4096 only**: Server always runs on this port
3. **Security first**: Firewall rules restrict access to IPs in `ALLOWED_IPS`
4. **Script preference**: Use `secure_opencode.sh` over manual commands when available

## Operations

### Start Server

**Preferred method** (handles firewall + server):
```bash
./secure_opencode.sh
```

**Manual method** (only if script fails):
```bash
# First check if already running
pgrep -f "opencode serve" && echo "Already running"

# Start with explicit bind
opencode serve --hostname 0.0.0.0 --port 4096 --print-logs --log-level INFO
```

### Check Status

```bash
# Check if server is running
pgrep -f "opencode serve" && echo "Running" || echo "Stopped"

# Check what's listening on port 4096
ss -tlnp | grep 4096

# Check firewall rules for port 4096
sudo iptables -L INPUT -n | grep 4096
```

### View Logs

```bash
# If running with --print-logs, logs go to stdout
# For systemd/service setups, check:
journalctl -u opencode -f 2>/dev/null || echo "Not a systemd service"
```

### Stop Server

```bash
# Graceful stop
pkill -f "opencode serve"

# Force kill if needed
pkill -9 -f "opencode serve"
```

### Update Firewall Rules

```bash
# Re-run the setup script (reloads .env and applies rules)
./secure_opencode.sh

# Or manually check/update:
# View current rules
sudo iptables -L INPUT -n --line-numbers | grep 4096

# Remove old rules (replace N with line number)
sudo iptables -D INPUT N

# Add new allow rule
sudo iptables -A INPUT -p tcp -s <IP> --dport 4096 -j ACCEPT

# Add drop rule for others
sudo iptables -A INPUT -p tcp --dport 4096 -j DROP
```

### Update Configuration

Edit `.env` file:
```bash
# View current config
cat .env

# Edit (requires workdir)
# Update OPENCODE_SERVER_PASSWORD and/or ALLOWED_IPS
# ALLOWED_IPS format: space-separated list like "YOUR_IP_HERE 192.168.1.100"
```

## Troubleshooting

**Cannot connect from external IP:**
1. Check firewall: `sudo iptables -L INPUT -n | grep 4096`
2. Verify server is bound to 0.0.0.0: `ss -tlnp | grep 4096`
3. Confirm IP is in `ALLOWED_IPS` in `.env`
4. Re-run `secure_opencode.sh`

**Port already in use:**
```bash
# Find what's using port 4096
lsof -i :4096

# Kill existing process
kill $(lsof -t -i:4096)
```

**Permission denied on iptables:**
- Commands need sudo - script handles this internally
- If running manually, prefix with `sudo`

## Security Notes

- **IP Whitelisting**: Only IPs in `ALLOWED_IPS` can connect
- **Default Deny**: All other IPs are blocked via iptables DROP rule
- **Password**: Set via `OPENCODE_SERVER_PASSWORD` in `.env`
- **No Git**: This is not a git repo - no version control

## Script Reference: secure_opencode.sh

The script does:
1. Load `.env` variables
2. Clear old iptables rules for port 4096
3. Add ACCEPT rules for each IP in `ALLOWED_IPS`
4. Add DROP rule for all other traffic to port 4096
5. Start `opencode serve --hostname 0.0.0.0 --port 4096 --print-logs --log-level INFO`

If modifying the script, preserve this order: ACCEPT rules before DROP rule.
