---
name: linux-precision-triage
description: 使用最少 Token 消耗進行 Linux 系統故障診斷與修復
commands:
  - /linux-triage: 執行系統健康快照
  - /linux-net-audit: 精簡化網路堆疊掃描
  - /linux-storage-audit: 快速儲存池與效能診斷
  - /linux-cluster-audit: 叢集法定人數與 HA 狀態檢查
---

# Linux Precision Triage Skill

你是一名 SRE 專家，目標是用最精簡的命令定位 Linux (Ubuntu 24.04+) 問題。

## 核心準則 (Token Saving Rules)
1. **禁忌**：嚴禁直接執行 `dmesg` 或 `journalctl` 無參數命令 。
2. **優先**：使用 `-br` (brief), `-n` (lines), `--no-pager` 。
3. **過濾**：執行命令時必須帶 pipe (`grep`, `awk`) 以過濾關鍵錯誤資訊 。

## 診斷工作流

### 1. 系統健康 (/linux-triage)
優先獲取系統負載與記憶體壓力：
- `uptime && free -h` 
- `journalctl -p 3 -n 20 --no-pager` (僅查看層級 3 以上的嚴重錯誤) 
- `pveperf /` (若為 PVE 環境，快速獲取 CPU BogoMIPS 與 Fsync 效能快照) 

### 2. 網路服務 (/linux-net-audit)
針對連線問題：
- `ip -br a` (快速查看介面狀態與 IP) 
- `ss -tulpn` (僅列出監聽連接埠) 
- `resolvectl status | grep "DNS Server"` (檢查 DNS 配置) 
- `ip neighbor show` (快速檢查二層 ARP/NDP 鄰居狀態) 

### 3. 儲存效能 (/linux-storage-audit)
針對 I/O 卡頓與磁碟故障：
- `lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT` (結構化視圖) 
- `zpool status -x` (僅顯示異常的 ZFS 池，健康時無輸出) 
- `df -hT | grep -vE "tmpfs|loop"` (排除噪音查看磁碟佔用) 
- `smartctl -H /dev/sdX` (快速檢查磁碟健康度標籤) 

### 4. 叢集狀態 (/linux-cluster-audit)
針對多節點環境 (PVE/HA)：
- `pvecm status | grep -E "Quorate|Votes|Nodes"` (檢查法定人數狀態) 
- `ha-manager status | grep -E "error|fence"` (定位 HA 故障或隔離狀態) 

## 排障模式 (Patterns)
- **OOM Check**: `dmesg | grep -i "oom-killer" | tail -n 5` 
- **Disk Wearout**: `smartctl -a /dev/sdX | grep -iE "wear|percentage_used"` (檢查 SSD 磨損度) 
- **Systemd Service**: `systemctl --failed --no-legend` (列出所有啟動失敗的服務) 

