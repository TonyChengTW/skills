---
name: pve-ufw-manager
description: Proxmox VE 虛擬化環境 UFW 防火牆管理
commands:
  - /pve-ufw-status: 檢查防火牆狀態
  - /pve-ufw-apply: 套用新防火牆規則
  - /pve-ufw-dry-run: 預覽即將套用的規則
  - /pve-ufw-rollback: Rollback 到上一版本
  - /pve-ufw-logs: 查看防火牆日誌
---

# PVE UFW Manager Skill

## 概述

專精於 Proxmox VE 主機上的 UFW 防火牆自動化管理的技能，提供安全、可 rollback 的防火牆規則管理框架。

## 核心工具

- `ufw` - Ubuntu/Debian 防火牆管理工具
- `iptables` - 底層 netfilter 規則查詢
- `journalctl` - 系統日誌查閱
- `logger` - 日誌寫入

## 適用的 Proxmox VE 環境

- Proxmox VE 7.x / 8.x / 9.x
- 基於 Debian 的 Linux 發行版
- 需要 UFW 管理介面

## 常用工作流

### 1. 防火牆狀態檢查
```bash
ufw status verbose
ufw status numbered
iptables -L -n -v
```

### 2. 預覽即將套用的規則 (Dry-run)
```bash
ufw-hvm-manager.sh --dry-run
```

### 3. 套用新規則
```bash
ufw-hvm-manager.sh --apply
```

### 4. 查看日誌
```bash
ufw-hvm-manager.sh --status
journalctl -u ufw -n 50
tail -f /var/log/pve/ufw-hvm-manager.log
```

### 5. Rollback 到上一版本
```bash
ufw-hvm-manager.sh --rollback
```

## 常用故障排除

### UFW 無法啟動
```bash
ufw disable
ufw reset
ufw-hvm-manager.sh --apply
```

### 規則未生效
```bash
ufw reload
iptables -L -n | grep <port>
```

### 連線被擋
```bash
ufw status numbered
ufw delete <rule_number>
```

## 腳本位置

主腳本: `scripts/ufw-hvm-manager.sh`

## 相關檔案

- `reference/ufw-ports.md` - 常用端口參考
<skill_files>

</skill_files>
