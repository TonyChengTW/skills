# Additional Proxmox Troubleshooting (Reddit/Community)

## Network Issues

### Network Connection Keeps Dropping After Reboot
- Check physical: swap ethernet cables, try different switch ports
- Check host logs: `journalctl -b` or `dmesg`
- ACPI BIOS errors in logs may indicate hardware issues
- Last resort: wipe and reinstall (some users resolved with clean Proxmox 9.x install)

### Network Interface Shows DOWN with No LOWER_UP
- Physical: Check cable, try different NIC slot
- Realtek NICs may have kernel compatibility issues
- Commands to try:
  ```bash
  ip link set enp34s0 up
  dhclient enp34s0
  ```
- Check `/etc/network/interfaces` for configuration errors

### Multiple Gateways Problem
- Each network interface should only have ONE gateway
- Having multiple gateways causes routing conflicts
- Use separate bridges or routes instead

### Cluster Using Wrong Network for Corosync
- During cluster creation, corosync uses the IP of the selected bridge
- Edit `/etc/pve/corosync.conf` to specify correct ring0_addr
- After changing IPs, update `/etc/pve/.members` on all nodes if needed

## Cluster and Quorum Issues

### Multicast/IGMP Snooping Causing Cluster Problems
- Linux bridge enables IGMP snooping by default
- Can cause multicast packet loss and quorum issues
- Quick fix: disable on corosync bridge
  ```bash
  echo 0 > /sys/class/net/vmbr0/bridge/multicast_snooping
  ```
- Permanent fix: Configure bridge to know multicast router port in `/etc/network/interfaces`:
  ```
  post-up echo 2 > /sys/class/net/vmbr0/brport/multicast_router
  ```

### VMs Showing as "Unknown" After Power Outage
- Reset cluster member states:
  ```bash
  systemctl restart pve-cluster
  ```
- Check `/etc/pve/.members` for correct node info
- May need to restart services in order:
  ```bash
  systemctl restart corosync pve-cluster pvedaemon pveproxy
  ```

### Cluster Offline / Quorum Lost
- Check network: Corosync should have dedicated NIC when possible
- Storage hanging can also cause cluster issues
- Collect from all nodes:
  - `ip a`, `ip route`
  - `pvecm status`
  - `journalctl` entries before/during event
  - PVE version from all nodes

## Storage Issues

### Physical Disk Not Recognized
- Check if disk shows in Windows but not Proxmox
- May need to initialize/partition disk first
- Check with `lsblk` and `fdisk -l`
- For passthrough: disk must not have partitions

### Storage Pool Full but No Alerts
- Verify `pvesm` alert thresholds configured
- Check `pveperf` for I/O latency affecting alert triggers

## VM and Container Issues

### VM Management Shows "?" Question Mark
- Restart pvedaemon service:
  ```bash
  systemctl restart pvedaemon
  ```
- Check VM config integrity in `/etc/pve/nodes/<node>/qemu-server/`
- May need to reload cluster configuration

### LXC Container Issues
- Check mount points and permissions
- Test with: `lxc-start -n <ctid> -F -l DEBUG`
- Common issues: broken root filesystem, mount point permissions

### VM Losing Network When Another VM Starts
- Check IOMMU groups: network card and passthrough device may be in same group
- Verify with: `find /sys/kernel/iommu/ -type f -name "*devices*"`
- May need different PCIe slot or disable passthrough

## Hardware and Passthrough

### GPU Passthrough Issues (NVIDIA, AMD, etc.)
- Ensure IOMMU enabled in BIOS and kernel cmdline
- Check GPU is in separate IOMMU group
- Disable ballooning for GPU VMs
- Add to VM config:
  ```
  args: -cpu host,hv_passthrough,hv_vendor_id=proxmox,kvm=off
  ```
- For NVIDIA: may need `vga: none` and proper OVMF setup

### Integrated Graphics (iGPU) Passthrough
- More complex due to CPU integration
- May cause host crashes or driver issues in VM
- Try different PCIe slot configurations

## Service and Daemon Issues

### Services Not Starting After Reboot
- Check service status: `systemctl status <service>`
- Review logs: `journalctl -u <service> -n 50`
- Common fix sequence:
  ```bash
  systemctl restart corosync
  systemctl restart pve-cluster
  systemctl restart pvedaemon
  systemctl restart pveproxy
  systemctl restart pve-ha-lrm
  systemctl restart pve-ha-crm
  ```

### Web UI Not Accessible
- Check services: `systemctl status pveproxy pvedaemon`
- Verify time sync: `chronyc tracking`
- Check `/var/log/pveproxy/` for errors
- Try clearing browser cache/cookies

## Two-Node Cluster Specific Issues

### 2-Node Cluster Quorum Issues
- Use two-node quorum override in `/etc/pve/corosync.conf`:
  ```
  quorum {
    provider: corosync_votequorum
    two_node: 1
  }
  ```
- Common issue: "got timeout when trying to ensure cluster certificates and base file hierarchy is set up - no quorum (yet)"
- Fix:
  ```bash
  pvecm updatecerts
  systemctl restart pvedaemon pveproxy
  ```
- After fixes, restart both nodes and clear browser cache

### Node Completely Unreachable in Cluster
- Symptoms: Ping, SSH, Corosync all unreachable
- Check physical switch port issues (try different port)
- Check speed/duplex negotiation issues
- Try connecting with different cables/ports
- Verify network config: `ip a`, `ip route`

## Network Performance

### Slow GUI and High Latency on Some Nodes
- Check network hardware offloading (TSO/GSO):
  ```bash
  ethtool -K vmbr0 tso off
  ethtool -K vmbr0 gso off
  ```
- Verify MTU matches on switch and vmbr0
- Use iperf to test each network segment:
  - Node to node
  - Host to guest
  - Guest to guest on same host
- Use Virtio drivers for VM networking
- Monitor PPS (Packets Per Second)

### Network Speed Tests Show Odd Results
- Test with iperf3 instead of speedtest.net
- iperf3 server: `iperf3 -s`
- iperf3 client: `iperf3 -c <server-ip>`
- Test segments: guest→host, host→router, router→world

## API and SDN Issues

### HTTP API "no sdn vnet ID specified" Error
- Error message is misleading - not actually an SDN issue
- Use `--data-urlencode` instead of `--data` in curl:
  ```bash
  curl -X PUT -H 'Authorization: PVEAPIToken=user@pve!secret' \
    --data-urlencode "net0=virtio=XX:XX:XX:XX:XX:XX,bridge=vmbr1,firewall=1,tag=10" \
    "https://host.example.com:8006/api2/json/nodes/host/qemu/133/config"
  ```

## Backup and Recovery

### When to Rebuild from Scratch
- If troubleshooting reveals multiple systemic issues
- Network issues that persist after trying multiple fixes
- Consider if clean install would be faster than extensive debugging
- Document configuration before rebuilding
- Test VM backups before migration

## Common Proxmox Mistakes (r/ProxmoxQA)

### ZFS RAM Planning
- ZFS requires significant RAM (1GB per 1TB raw storage recommended)
- Insufficient RAM causes performance degradation and stability issues
- Calculate: at least 32GB for meaningful ZFS usage

### ZFS RAIDZ for VM Storage
- RAIDZ has poor write performance for VM workloads
- Use mirrored vdevs or SSD-based storage for VM disks
- Consider local-lvm or plain ZFS with mirrored vdevs

### CPU Type "host" Issues
- Using "host" CPU type provides best performance but breaks migration
- Use "kvm64" or "kvm" for migration compatibility
- Only use "host" when absolutely necessary (GPU passthrough, etc.)

### HA Without Prerequisites
- HA requires proper cluster setup with at least 3 nodes
- Two-node clusters need quorum device (qdevice)
- Without proper fencing, HA can cause split-brain issues

### Docker on Proxmox Host
- Running Docker directly on PVE kernel is not recommended
- Run Docker in a VM instead (CT is fine but VM is safer)
- Exception: some monitoring tools require host-level access

### No Monitoring
- Install monitoring before issues occur
- Use SNMP traps, email alerts, and forced checkins
- Avoid installing database agents directly on nodes

### Running Services on Hypervisor
- Don't run services directly on PVE host
- Use VMs or containers for all services
- Keep hypervisor clean for virtualization only

## Firewall Issues (Networking Forum)

### VM Firewall Blocking Outgoing Traffic
- Enable firewall on VM NIC blocks all traffic even with ACCEPT rules
- Root cause: connection tracking zone not properly set
- Fix: Add iptables rule:
  ```bash
  iptables -t raw -I PREROUTING -i fwbr+ -j CT --zone 1
  ```
- Or add to `/etc/network/interfaces`:
  ```
  post-up iptables -t raw -I PREROUTING -i fwbr+ -j CT --zone 1
  ```

### Firewall Makes Host Unreachable
- Enabling firewall with ACCEPT everywhere can still cause issues
- Check iptables rules: `iptables -L -v -n`
- Check NAT rules: `iptables -t nat -L -v -n`
- Use `iptables-save` to see all generated rules
- Reboot required to fully reset firewall state in some cases

### pfSense/OPNsense Performance Issues
- FreeBSD-based firewalls may have performance issues on Proxmox
- Try VirtIO driver for better performance
- Disable hardware offloading on both host and guest
- Consider using different firewall solution if issues persist

### Proxmox Firewall Basics
- Datacenter-level rules apply to all nodes
- Node-level rules apply to specific node
- VM/CT rules apply to specific virtual machines
- Use `iptables-save` to see all generated rules
- Check PVEFW-FORWARD chain for VM traffic issues

## Installation Issues (Installation Forum)

### No Network After Installation
- Check if cable is properly connected (NO-CARRIER)
- Verify NIC is detected: `ip link`
- Check `/etc/network/interfaces` for correct config
- Try different network cable or switch port

### Cannot Access Web UI After Install
- Verify IP address assigned: `ip addr`
- Check if services are running: `systemctl status pveproxy pvedaemon`
- Ensure browser uses HTTPS not HTTP
- Check firewall: `iptables -L PVEFW-FORWARD -v -n`

### Installation Without Internet
- Proxmox needs internet during installation for package setup
- Install with proper network connection first
- After installation, configure offline repos if needed

### Hardware Compatibility Issues
- DDR5 RAM may cause instability - check BIOS updates
- NVIDIA GPUs may cause installation issues - try nomodeset
- Wi-Fi/Bluetooth may interfere - disable in BIOS

### Boot Issues After Installation
- "Loading initial ramdisk" stuck - check disk with `fsck`
- Volume group errors - check `lvs` and LVM status
- Try older kernel: `proxmox-boot-tool refresh`

### IP Configuration Issues
- Static IP format: `address 192.168.1.100/24`
- Gateway format: `gateway 192.168.1.1`
- Avoid .local TLD (reserved for mDNS)
- Use proper CIDR notation (/24 not /255.255.255.0)

### VM Network Not Working
- VM can't get IP: Check DHCP server, switch port
- VM can't ping gateway: Check bridge config
- VM can't reach internet: Check masquerading/NAT rules