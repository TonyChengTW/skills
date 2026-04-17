#!/bin/bash
# PVE UFW Manager - Secure firewall management for Proxmox VE hosts
# Author: OpenCode Assistant
# Version: 1.0.0

set -euo pipefail

# Configuration
IPRANGE="1.2.3.4 5.6.7.8 9.10.11.12"
PORTRANGE_TCP="22,80,443,9100,9221,3128"
PORTRANGE_UDP="161"
LOG_FILE="/var/log/pve/ufw-hvm-manager.log"
BACKUP_DIR="/etc/ufw/backups"
MAX_BACKUPS=5

# Proxmox VE default rules to preserve
PVE_DEFAULT_RULES=(
    "22/tcp"
    "8006/tcp"
    "8007/tcp"
    "10.0.0.0/8"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" >> "$LOG_FILE"
    
    # Also echo to console for immediate feedback
    case "$level" in
        "INFO")  echo -e "${GREEN}[INFO]${NC} $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" ;;
        *)       echo -e "[${level}] $message" ;;
    esac
}

# Check if script is run as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_message "ERROR" "This script must be run as root"
        exit 1
    fi
}

# Check if UFW is installed
check_ufw_installed() {
    if ! command -v ufw &> /dev/null; then
        log_message "ERROR" "UFW is not installed. Please install it first: apt install ufw"
        exit 1
    fi
    
    if ! dpkg -l | grep -q ufw; then
        log_message "ERROR" "UFW package not found in dpkg"
        exit 1
    fi
    
    log_message "INFO" "UFW is installed"
}

# Backup current UFW rules
backup_rules() {
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/ufw.backup.${timestamp}"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Backup UFW rules
    ufw status verbose > "${backup_file}.status"
    cp /etc/ufw/user.rules "${backup_file}.user.rules" 2>/dev/null || true
    cp /etc/ufw/user6.rules "${backup_file}.user6.rules" 2>/dev/null || true
    cp /etc/ufw/before.rules "${backup_file}.before.rules" 2>/dev/null || true
    cp /etc/ufw/before6.rules "${backup_file}.before6.rules" 2>/dev/null || true
    cp /etc/ufw/after.rules "${backup_file}.after.rules" 2>/dev/null || true
    cp /etc/ufw/after6.rules "${backup_file}.after6.rules" 2>/dev/null || true
    
    # Create a manifest file
    echo "Backup created at: $(date)" > "${backup_file}.manifest"
    echo "UFW status:" >> "${backup_file}.manifest"
    ufw status verbose >> "${backup_file}.manifest"
    
    log_message "INFO" "Backup created: ${backup_file}.*"
    
    # Clean old backups, keeping only the most recent MAX_BACKUPS
    local backup_count
    backup_count=$(ls -1 "${BACKUP_DIR}"/ufw.backup.* 2>/dev/null | wc -l)
    if [[ $backup_count -gt $MAX_BACKUPS ]]; then
        local to_remove
        to_remove=$((backup_count - MAX_BACKUPS))
        ls -1t "${BACKUP_DIR}"/ufw.backup.* | tail -n "$to_remove" | xargs -r rm -f
        log_message "INFO" "Cleaned up old backups, keeping ${MAX_BACKUPS} most recent"
    fi
}

# Validate IP addresses in IPRANGE
validate_ip_range() {
    local ip
    for ip in $IPRANGE; do
        # Simple validation - could be enhanced
        if [[ ! $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            log_message "ERROR" "Invalid IP address format: $ip"
            return 1
        fi
    done
    return 0
}

# Validate port ranges
validate_port_range() {
    local range="$1"
    local protocol="$2"
    
    IFS=',' read -ra PORTS <<< "$range"
    for port in "${PORTS[@]}"; do
        if [[ ! $port =~ ^[0-9]+$ ]] || [[ $port -lt 1 ]] || [[ $port -gt 65535 ]]; then
            log_message "ERROR" "Invalid ${protocol} port: $port"
            return 1
        fi
    done
    return 0
}

# Show dry-run preview of rules that would be applied
dry_run_preview() {
    log_message "INFO" "=== DRY-RUN MODE: Previewing rules to be applied ==="
    
    local ip
    for ip in $IPRANGE; do
        local port
        IFS=',' read -ra PORTS <<< "$PORTRANGE_TCP"
        for port in "${PORTS[@]}"; do
            echo "ufw allow from $ip to any port $port proto tcp"
        done
        
        IFS=',' read -ra PORTS <<< "$PORTRANGE_UDP"
        for port in "${PORTS[@]}"; do
            echo "ufw allow from $ip to any port $port proto udp"
        done
    done
    
    log_message "INFO" "=== End of dry-run preview ==="
}

# Apply the firewall rules
apply_rules() {
    log_message "INFO" "Starting to apply firewall rules..."
    
    # Backup current rules first
    backup_rules
    
    # Reset UFW to ensure clean state (optional - comment out if you want to preserve existing rules)
    # log_message "INFO" "Resetting UFW to clean state..."
    # ufw --force reset
    
    # Set default policies
    log_message "INFO" "Setting default policies..."
    ufw default deny incoming
    ufw default allow outgoing
    log_message "INFO" "Default policies set: deny incoming, allow outgoing"
    
    # Apply rules for each IP in IPRANGE
    local ip
    for ip in $IPRANGE; do
        log_message "INFO" "Applying rules for source IP: $ip"
        
        # Apply TCP rules
        local port
        IFS=',' read -ra PORTS <<< "$PORTRANGE_TCP"
        for port in "${PORTS[@]}"; do
            if ufw allow from "$ip" to any port "$port" proto tcp; then
                log_message "INFO" "Added rule: allow from $ip to any port $port proto tcp"
            else
                log_message "ERROR" "Failed to add rule: allow from $ip to any port $port proto tcp"
                return 1
            fi
        done
        
        # Apply UDP rules
        IFS=',' read -ra PORTS <<< "$PORTRANGE_UDP"
        for port in "${PORTS[@]}"; do
            if ufw allow from "$ip" to any port "$port" proto udp; then
                log_message "INFO" "Added rule: allow from $ip to any port $port proto udp"
            else
                log_message "ERROR" "Failed to add rule: allow from $ip to any port $port proto udp"
                return 1
            fi
        done
    done
    
    # Add Proxmox VE default rules (comment out if not needed)
    log_message "INFO" "Adding Proxmox VE default rules..."
    ufw allow 22/tcp comment 'SSH'
    ufw allow 8006/tcp comment 'PVE Web Interface'
    ufw allow 8007/tcp comment 'PVE Proxy'
    ufw allow from 10.0.0.0/8 comment 'Private Network'
    
    # Enable UFW
    log_message "INFO" "Enabling UFW..."
    if ufw --force enable; then
        log_message "INFO" "UFW enabled successfully"
    else
        log_message "ERROR" "Failed to enable UFW"
        return 1
    fi
    
    # Show final status
    log_message "INFO" "Final UFW status:"
    ufw status verbose | while IFS= read -r line; do
        log_message "INFO" "$line"
    done
    
    log_message "INFO" "Firewall rules applied successfully"
    return 0
}

# Rollback to a previous backup
rollback_rules() {
    log_message "INFO" "Starting rollback procedure..."
    
    # List available backups
    local backups
    backups=$(ls -1t "${BACKUP_DIR}"/ufw.backup.*.manifest 2>/dev/null || true)
    
    if [[ -z "$backups" ]]; then
        log_message "ERROR" "No backups found in ${BACKUP_DIR}"
        return 1
    fi
    
    # Show available backups
    log_message "INFO" "Available backups:"
    local i=1
    for backup in $backups; do
        local timestamp
        timestamp=$(basename "$backup" | cut -d'.' -f3-4)
        echo "  $i) $timestamp"
        ((i++))
    done
    
    # Ask user which backup to restore to (or use most recent)
    local choice
    if [[ "$#" -eq 0 ]]; then
        # No argument provided, ask user
        read -p "Select backup to restore to (1-${#backups[@]}, or 'latest' for most recent): " choice
    else
        choice="$1"
    fi
    
    local selected_backup
    if [[ "$choice" == "latest" ]] || [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -le ${#backups[@]} ]]; then
        if [[ "$choice" == "latest" ]]; then
            selected_backup=$(echo "$backups" | head -n1)
        else
            selected_backup=$(echo "$backups" | sed -n "${choice}p")
        fi
    else
        log_message "ERROR" "Invalid selection"
        return 1
    fi
    
    # Extract backup name without extension
    local backup_base
    backup_base=$(basename "$selected_backup" .manifest)
    backup_base="${BACKUP_DIR}/${backup_base}"
    
    log_message "INFO" "Rolling back to backup: $backup_base"
    
    # Disable UFW before restoring
    ufw disable
    
    # Restore UFW configuration files
    if [[ -f "${backup_base}.user.rules" ]]; then
        cp "${backup_base}.user.rules" /etc/ufw/user.rules
        log_message "INFO" "Restored user.rules"
    fi
    
    if [[ -f "${backup_base}.user6.rules" ]]; then
        cp "${backup_base}.user6.rules" /etc/ufw/user6.rules
        log_message "INFO" "Restored user6.rules"
    fi
    
    if [[ -f "${backup_base}.before.rules" ]]; then
        cp "${backup_base}.before.rules" /etc/ufw/before.rules
        log_message "INFO" "Restored before.rules"
    fi
    
    if [[ -f "${backup_base}.before6.rules" ]]; then
        cp "${backup_base}.before6.rules" /etc/ufw/before6.rules
        log_message "INFO" "Restored before6.rules"
    fi
    
    if [[ -f "${backup_base}.after.rules" ]]; then
        cp "${backup_base}.after.rules" /etc/ufw/after.rules
        log_message "INFO" "Restored after.rules"
    fi
    
    if [[ -f "${backup_base}.after6.rules" ]]; then
        cp "${backup_base}.after6.rules" /etc/ufw/after6.rules
        log_message "INFO" "Restored after6.rules"
    fi
    
    # Reload UFW to apply restored rules
    ufw reload
    
    # Re-enable UFW if it was enabled in the backup
    if grep -q "Status: active" "${backup_base}.status" 2>/dev/null; then
        ufw enable
        log_message "INFO" "UFW re-enabled after rollback"
    else
        log_message "INFO" "UFW left disabled as per backup state"
    fi
    
    log_message "INFO" "Rollback completed successfully"
    return 0
}

# Show current UFW status and recent log entries
show_status() {
    log_message "INFO" "=== Current UFW Status ==="
    ufw status verbose
    
    log_message "INFO" "=== Recent Log Entries ==="
    if [[ -f "$LOG_FILE" ]]; then
        tail -n 20 "$LOG_FILE"
    else
        echo "Log file not found: $LOG_FILE"
    fi
    
    log_message "INFO" "=== Available Backups ==="
    ls -1t "${BACKUP_DIR}"/ufw.backup.*.manifest 2>/dev/null | head -n 5 | while read -r backup; do
        local timestamp
        timestamp=$(basename "$backup" .manifest | cut -d'.' -f3-4)
        echo "  $timestamp"
    done
}

# Display help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --dry-run     Preview rules that would be applied (no changes made)
  --apply       Apply the firewall rules (default action)
  --rollback    Rollback to a previous backup
  --status      Show current UFW status and recent logs
  --help        Display this help message

Examples:
  $(basename "$0") --dry-run
  $(basename "$0") --apply
  $(basename "$0") --rollback
  $(basename "$0") --rollback latest
  $(basename "$0") --status

Description:
  This script manages UFW firewall rules for Proxmox VE hosts.
  It allows specific IP ranges to access essential services including:
  - SSH (22/tcp)
  - HTTP (80/tcp)
  - HTTPS (443/tcp)
  - node_exporter (9100/tcp)
  - PVE exporter (9221/tcp)
  - spiceproxy (3128/tcp)
  - SNMP (161/udp)

  The script preserves Proxmox VE default rules for:
  - SSH (22/tcp)
  - PVE Web Interface (8006/tcp)
  - PVE Proxy (8007/tcp)
  - Private Network (10.0.0.0/8)

  Features:
  - Dry-run mode to preview changes
  - Automatic backup before applying changes
  - Rollback capability with history (keeps last 5 backups)
  - Comprehensive logging to /var/log/pve/ufw-hvm-manager.log
EOF
}

# Main script execution
main() {
    # Default action is apply
    local action="apply"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                action="dry_run"
                shift
                ;;
            --apply)
                action="apply"
                shift
                ;;
            --rollback)
                action="rollback"
                shift
                ;;
            --status)
                action="status"
                shift
                ;;
            --help)
                action="help"
                shift
                ;;
            *)
                log_message "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Execute requested action
    case "$action" in
        "dry_run")
            check_root
            check_ufw_installed
            validate_ip_range
            validate_port_range "$PORTRANGE_TCP" "TCP"
            validate_port_range "$PORTRANGE_UDP" "UDP"
            dry_run_preview
            ;;
        "apply")
            check_root
            check_ufw_installed
            validate_ip_range
            validate_port_range "$PORTRANGE_TCP" "TCP"
            validate_port_range "$PORTRANGE_UDP" "UDP"
            apply_rules
            ;;
        "rollback")
            check_root
            check_ufw_installed
            rollback_rules "$@"
            ;;
        "status")
            check_root
            check_ufw_installed
            show_status
            ;;
        "help")
            show_help
            ;;
        *)
            log_message "ERROR" "Unknown action: $action"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
