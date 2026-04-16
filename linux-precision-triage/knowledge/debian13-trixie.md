# Debian 13 (Trixie) Troubleshooting Knowledge

## Upgrade Issues

### Interrupted Remote Upgrades
- SSH upgrade interruption can lock you out of remote systems
- Before upgrading remotely, update OpenSSH to version >= 1:9.2p1-2+deb12u7
- Use in-band console or IPMI for remote upgrades when possible

### /boot Partition Too Small
- Kernel and firmware packages have increased in size
- Systems installed with Debian 10 (buster) or earlier are likely affected
- Before upgrade: ensure /boot is at least 768 MB with ~300 MB free
- If /boot is LVM: use `lvextend -L+500M /dev/mapper/vg-lv` to resize

### tmpfs Default for /tmp
- From Trixie, /tmp defaults to tmpfs (stored in memory)
- Applications expecting disk-based /tmp may fail
- Check: `systemctl status tmp.mount`
- To disable tmpfs for /tmp, add to /etc/fstab:
  ```
  /tmp none tmpfs defaults 0 0
  ```

## SSH and Authentication

### OpenSSH No Longer Reads ~/.pam_environment
- SSH connections may behave differently after upgrade
- Set environment variables in /etc/environment or ~/.profile instead

### OpenSSH No Longer Supports DSA Keys
- If using DSA keys, migrate to Ed25519 or RSA
- Generate new key: `ssh-keygen -t ed25519`

### last/lastb/lastlog Commands Replaced
- These commands are now provided by wtmpdb package
- Use `wtmpdb last` as replacement
- Install: `apt install wtmpdb`

### ping No Longer Runs with Elevated Privileges
- ping requires CAP_NET_RAW capability
- Use `ping -k cap_net_raw` or set capabilities:
  ```bash
  setcap cap_net_raw+ep /bin/ping
  ```
- Or use fping as alternative

## System Configuration

### /etc/sysctl.conf No Longer Honored
- systemd-sysctl no longer reads /etc/sysctl.conf
- Use /etc/sysctl.d/*.conf files instead
- Create /etc/sysctl.d/99-custom.conf for custom settings
- Apply: `sysctl --system`

### Network Interface Names May Change
- Two circumstances cause different naming from Bookworm:
  1. System with only one ethernet device gets predictable names disabled
  2. Boot without systemd Predictable Network Names enabled
- Check: `ls /sys/class/net/`
- To preserve old names, edit /etc/default/grub:
  ```
  GRUB_CMDLINE_LINUX_DEFAULT="net.ifnames=0 biosdevname=0"
  ```
- Then: `update-grub && reboot`

### System is tainted: unmerged-bin
- This warning appears when /usr has files from different package sources
- Typically occurs with third-party repos or manual installs
- Usually harmless but may affect support

## Storage and Filesystems

### Encrypted Filesystems Need systemd-cryptsetup
- Auto-discovering and mounting moved to systemd-cryptsetup
- Install: `apt install systemd-cryptsetup`
- For LUKS: ensurecrypttab is properly configured

### tmp and var/tmp Regularly Cleaned
- systemd-tmpfiles clean these directories daily
- Default age: 10 days for /tmp, 30 days for /var/tmp
- Check: `systemctl status systemd-tmpfiles-clean.timer`
- Adjust in /etc/tmp.conf or /etc/systemd/system/*.service.d/

## Database and Services

### MariaDB Major Version Upgrade
- Only works reliably after clean shutdown
- Before upgrade: `mysqladmin shutdown`
- After upgrade: `mysql_upgrade`

### RabbitMQ Issues
- HA queues no longer supported
- Cannot directly upgrade from Bookworm
- May need fresh install and migration

## Package Management

### dpkg Warning: Unable to Delete Old Directory
- Usually occurs after package removal
- Check: `dpkg -l | grep "^.h"`
- Fix: `dpkg --configure -a`

### Skip-upgrades Not Supported
- Cannot skip major version upgrades
- Must upgrade sequentially: Bookworm → Trixie

## Security

### Security Support Limitations
- Some packages don't have minimal backports for security issues
- Check support status: `apt install debian-security-support`
- Run: `debsecurity-status`

### Web Browsers and Rendering Engines
- Several browser engines have high vulnerability rates
- Keep browsers updated
- Consider using Flatpak versions for better isolation

## Systemd and Services

### WirePlumber New Configuration
- PipeWire's session manager has new config system
- May need to update custom configs in ~/.config/wireplumber/

### strongSwan Migration
- Migration to new charon daemon required
- Check /etc/swanctl/ and /etc/strongswan.conf configs

### Timezones in tzdata-legacy
- Legacy timezone data moved to separate package
- Install if needed: `apt install tzdata-legacy`

## Pre-Upgrade Checklist

1. Update OpenSSH before remote upgrade
2. Ensure /boot has 768MB+ free space
3. Check /etc/sysctl.conf needs migration to sysctl.d/
4. Review /etc/network/interfaces for interface name changes
5. Backup before upgrade
6. Test in VM before production upgrade
7. Check for custom service configs that may break
8. Review third-party repos compatibility

## Reddit r/debian Troubleshooting

### WiFi Connected But Webpages Don't Load
- Check DNS: `resolvectl status`
- Check routing: `ip route`
- Test DNS manually: `nslookup google.com`
- Try ping IP first: `ping 8.8.8.8`
- Check if connman is the network manager (common on some DEs)
- Check firewall rules: `iptables -L` or `nft list ruleset`

### APT/Sources Conflict Issues
- Error: "Conflicting values set for option Signed-By"
- Check for duplicate repo entries: `grep -r "signed-by" /etc/apt/sources.list.d/`
- Check /etc/apt/sources.list and all .list files in sources.list.d/
- For third-party repos (e.g., InfluxDB), check their key update notices
- Fix: Remove duplicate entries or update keyring packages
- Refresh: `apt update` after fixing

### SSD Not Detected During Installation
- Check if in AHCI mode in UEFI (not RAID)
- Disable Secure Boot
- Disable Fast Startup in Windows
- Try Ubuntu Live USB to verify hardware detection
- If Ubuntu works, load drivers manually in Debian installer
- Check NVMe mode settings in BIOS
- Try Ventoy or different USB creation tool

### PulseAudio Keeps Restarting
- Symptoms: Crackling sound, frequent reconnects in pavucontrol
- Check: `pulseaudio -v` for "Starting playback" stall
- Try with new user account (may be user config issue)
- Purge conflicting packages: timidity, speech-dispatcher
- Add to /etc/pulse/default.pa:
  ```
  load-module module-udev-detect tsched=0
  ```
- Add to /etc/pulse/daemon.conf:
  ```
  avoid-resampling = true
  default-sample-rate = 48000
  ```
- Check for hardware-specific ALSA issues

### Keyboard Not Responding After Suspend (Sony Vaio)
- Check keyboard controller: `dmesg | grep i8042`
- Add to /etc/default/grub:
  ```
  GRUB_CMDLINE_LINUX_DEFAULT="quiet splash i8042.direct i8042.dumbkbd"
  ```
- Run: `update-grub`
- Try different i8042 kernel parameters if above doesn't work

### Shutdown Hangs with Encrypted Volumes
- Systemd unmounts network mounts (DAVFS) before encrypted volumes
- Add _netdev to /etc/fstab for network mounts
- Add x-systemd.requires=cryptsetup.target to crypttab
- Check: `systemd-analyze blame` for slow units
- Add to crypttab options: `x-systemd-after=remote-fs.target`

### NVIDIA Driver Installation Issues
- Use Debian package: `apt install nvidia-driver firmware-misc-nonfree`
- Manual .run installation missing:
  - /etc/modprobe.d/ config files
  - nvidia-persistenced service
- Fix: Install via apt for proper integration
- If manual install: copy configs from /usr/share/nvidia/
- Check: `nvidia-smi` and `nvidia-settings`

### Boot Volume Size Assumptions
- /boot typically needs ~500MB+ with recent kernels
- Kernel and firmware packages have grown significantly
- Can use separate /boot or keep in root with enough space
- Check: `df -h /boot`

### Automatic Updates During Boot/Shutdown
- Check: `systemd-analyze blame`
- Uninstall: `apt remove unattended-upgrades`
- Disable in GNOME Software: Update Preferences
- Check DE update settings

### Network Manager Issues
- Common: connman, NetworkManager, systemd-networkd
- Check which is running: `systemctl status NetworkManager`
- For connman: `connmanctl` for interactive control
- Check interfaces: `ip link show`
- Check DNS: `cat /etc/resolv.conf`