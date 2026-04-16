# Corosync Operations and Troubleshooting

## Creating a Cluster with Multiple Network Links

Create cluster with dedicated corosync networks:
```bash
pvecm create <cluster-name> --link0 192.168.15.1,priority=15 --link1 192.168.40.1,priority=20
```

Add node with multiple links:
```bash
pvecm add <cluster-ip> --link0 192.168.15.2,priority=15 --link1 192.168.40.2,priority=20
```

## Changing Corosync IP Addresses

**Official method (PVE >= 4.x):**
1. Edit `/etc/pve/corosync.conf` directly (not via pmxcfs -l)
2. Change ring0_addr/ring1_addr for the node
3. Increment config_version
4. Restart: `systemctl restart corosync pve-cluster`

**Do NOT use** `pmxcfs -l` for routine changes - it can break the cluster.

## Authkey Issues

If corosync fails to start with "Cannot initialize CMAP service":
- Check `/etc/corosync/authkey` exists and is identical on all nodes
- Copy authkey from working node: `scp /etc/corosync/authkey node2:/etc/corosync/`
- Regenerate if needed: `corosync-keygen`

## Common Corosync Errors and Solutions

### "Token has not been received in X ms" (high numbers)
- Network latency too high (>5ms for LAN)
- Network congestion or packet loss
- Solution: Check network with `ping -c 500` between nodes, use dedicated NIC for corosync

### "Retransmit List" messages
- Network packet loss or congestion
- Duplicate ring addresses
- MTU mismatch between nodes
- Check switch spanning tree (RSTP) - disable on corosync ports

### "Cannot initialize CMAP service"
- Usually authkey mismatch or corruption
- Copy identical authkey to all nodes

### Service fails after IP change
- Old method: Stop pve-cluster and corosync, edit config, restart
- Better method: Edit while services running, config syncs automatically
- Ensure all nodes can reach new IPs

## Cluster Network Requirements

- Dedicated NICs recommended for corosync traffic
- Latency <5ms between all nodes (LAN performance)
- Multicast must be supported on network switches
- Firewall: Allow port 5405 (UDP) bidirectional
- Use separate VLANs for corosync if spanning tree enabled on switches

## Viewing Corosync Status

```bash
# Cluster status
pvecm status

# Node membership
pvecm nodes

# Detailed corosync info
corosync-cfgtool -n

# View config
cat /etc/pve/corosync.conf
```

## Removing a Node

1. Power off the failed node
2. From remaining node: `pvecm delnode <nodename>`
3. Clean up: Remove node entries from corosync.conf on all remaining nodes

## Emergency Local Mode

If cluster is broken and you need local access:
```bash
systemctl stop pve-ha-lrm pve-ha-crm corosync pve-cluster
pmxcfs -l
# Edit configuration in /etc/pve/
# When done: reboot or manually restart services
```

**Warning**: Never use local mode permanently - cluster config will diverge.

## Monitoring Corosync Health

```bash
# Watch corosync logs
journalctl -u corosync -f

# Check network links
corosync-cfgtool -s

# View ring status
pvecm status
```

## Service Restart Order

When restarting corosync services:
```bash
systemctl restart corosync
systemctl restart pve-cluster
systemctl restart pvedaemon
systemctl restart pveproxy
systemctl restart pve-ha-lrm
systemctl restart pve-ha-crm
```

## Time Synchronization

Corosync requires synchronized time:
```bash
# Install and enable chrony
apt install chrony
systemctl enable chrony
systemctl start chrony

# Verify sync
chronyc tracking
```