# Proxmox VE Troubleshooting Knowledge from Forum

## Disk and Storage Issues
- Check disk health with SMART: `smartctl -a /dev/sda`
- Look for critical SMART attributes:
  - Reallocated_Sector_Ct
  - Pending_Sector
  - Uncorrectable_Error_Ct
- Consider filesystem change if experiencing issues with XFS (try ext4 or ZFS)
- Verify storage configuration in `/etc/pve/storage.cfg`

## Network and Connectivity Problems
- CLI hanging/unresponsiveness often due to network misconfiguration
- Ensure VM and host are in compatible subnets for management access
- VLAN misconfigurations on managed switches can cause isolation after reboot
- Check if services are accessible locally via console when web UI fails
- For Corosync clusters:
  - Use dedicated NICs for Corosync communication when possible
  - Disable spanning tree (RSTP) on switch ports connected to Proxmox nodes
  - Avoid manually changing knet_mtu (auto-computed by Corosync)
  - Verify multicast support on network switches
  - Ensure firewall allows port 5405 (Corosync) bidirectional

## Time Synchronization
- Critical for cluster stability - install and configure chrony on all nodes
- Time differences >0.5s can cause corosync authentication failures
- Check time sync: `chronyc tracking` or `ntpq -p`

## Corosync and Cluster Specific Issues
- Retransmit storms often indicate network or configuration problems:
  - Check for duplicate IP addresses
  - Verify ring0/ring1 addresses in `/etc/pve/corosync.conf`
  - Ensure consistent MTU across cluster network
- After Corosync updates:
  - Verify `/etc/corosync/corosync.conf` and `/etc/pve/corosync.conf` are identical
  - Common failure: `/etc/pve` mount point not empty - move files and restart
- Cluster synchronization abnormally slow:
  - Use multiple network ports for Corosync redundancy
  - Separate physical interfaces exclusively for Corosync traffic
  - Monitor latency between nodes (should be <5ms for LAN performance)

## Web GUI Access Problems
- When unable to login to webui:
  1. Check if services are running: `systemctl status pveproxy pvedaemon`
  2. Verify time synchronization between nodes
  3. Restart in order: corosync → pve-cluster → pvedaemon → pveproxy
  4. Check logs: `journalctl -u pveproxy -u pvedaemon -f`
  5. Examine `/var/log/pveproxy/` for specific error messages
- "Connection Refused" after starting VMs often indicates:
  - VM DHCP client grabbing host's IP address
  - Solution: Configure VMs with static IPs instead of DHCP
  - Check VM network configuration in `/etc/netplan/` or `/etc/network/interfaces`

## HA and Resource Management
- When HA resources fail to start:
  - Check `ha-manager status` for resource state
  - Examine logs: `journalctl -u pve-ha-lrm -u pve-ha-crm`
  - Common causes: storage path inaccessibility, misconfigured resources
- For maintenance mode:
  - Enable: `ha-manager crm-command node-maintenance enable <nodename>`
  - Disable: `ha-manager crm-command node-maintenance disable <nodename>`

## Emergency Recovery
- When cluster loses quorum:
  - On remaining node: `pvecm expected 1` (temporarily)
  - Fix underlying issue (network, storage, etc.)
  - Restore proper quorum value: `pvecm expected <actual_node_count>`
- To remove failed node:
  - Ensure node is powered off
  - Run: `pvecm delnode <nodename>`
- For local recovery when node cannot join cluster:
  - Start corosync in local mode: `pmxcfs -l`
  - Edit configuration files directly in `/etc/pve`
  - Restart services normally after fix

## Performance Monitoring
- Use `pveperf /` for baseline storage performance:
  - FSYNCS/SECOND > 2000 indicates good SSD/Raid-BBU performance
  - < 200 suggests storage write performance issues
  - REGEX/SECOND > 300,000 expected for CPU performance
- Monitor real-time with `pvetop` for:
  - High IOWait or CPU Steal percentages
  - Memory pressure
  - Network utilization

## Log Investigation
- Task logs: `tail -f /var/log/pve/tasks/UPID*`
- System logs: `journalctl -u pve* -f`
- Corosync logs: `journalctl -u corosync -f`
- HA logs: `journalctl -u pve-ha-lrm -u pve-ha-crm`
- Proxy logs: `/var/log/pveproxy/{access.log,error.log}`

## Preventive Measures
- Regularly check SMART status on storage devices
- Monitor cluster time synchronization
- Review network switch logs for spanning tree events
- Keep Proxmox and Corosync packages updated (but test in lab first)
- Document cluster network topology and configuration
- Test backups and disaster recovery procedures regularly

