---
name: pve-cluster-doctor
description: Proxmox VE 虛擬化環境進階診斷與維護
commands:
  - /pve-vm-stuck: 處理無法關閉、鎖定或遷移掛起的 VM/LXC
  - /pve-health: 叢集法定人數、HA 狀態與系統效能快照
  - /pve-storage-audit: 存儲後端 (Ceph/ZFS/NFS) 離線與延遲診斷
  - /pve-quorum-fix: 叢集法定人數緊急修復與節點強制移除
---

# Proxmox Cluster Doctor Skill

專精於 Proxmox CLI 工具羣 (`qm`, `pct`, `pvesm`, `pvecm`, `pveceph`)。

## 核心診斷工作流

### 1. 虛擬機與容器救援 (/pve-vm-stuck)
針對受損或鎖定的資源：
- `qm status <vmid>` & `qm unlock <vmid>` (解除因備份或遷移失敗導致的設定鎖定) 。
- `pct stop <vmid> --skippedError` (強制停止容器) 。
- `qm monitor <vmid>` (進入 QEMU 監控界面檢查內部懸掛狀態) 。
- `tail -f /var/log/pve/tasks/UPID...` (追蹤特定作業 ID 的實時日誌以定位掛起位置) 。

### 2. 叢集與 HA 健康檢查 (/pve-health)
定位叢集通訊與自動切換問題：
- `pvecm status`: 檢查 `Quorate: Yes` 與節點票數 (Votes) 。
- `ha-manager status`: 查看 HA 資源狀態 (如 `fence`, `error`, `recovery`) 。
- `pveperf /`: 快速測試 `FSYNCS/SECOND` (目標應 > 200) 以確認硬體與快取效能是否達標 。
- `journalctl -u pve-ha-lrm -u pve-ha-crm -n 50`: 查看本地與叢集資源管理員錯誤 。

### 3. 存儲後端診斷 (/pve-storage-audit)
處理掛起的存儲或同步延遲：
- `pvesm status`: 檢查所有定義存儲的當前可用性 。
- `pveceph status` & `ceph health detail`: (若使用 Ceph) 快速定位 OSD 離線或數據平衡問題 。
- `zpool status -x`: (若使用 ZFS) 僅顯示異常的存儲池，健康時無輸出 。
- `pvesr status`: 檢查存儲複製 (Storage Replication) 是否超時或失敗 。

### 4. 叢集緊急救援 (/pve-quorum-fix)
當多數節點離線導致叢集唯讀或無法操作時：
- `pvecm expected 1`: 在剩餘節點強制設定法定人數為 1，以恢復設定修改權限 。
- `pvecm delnode <nodename>`: 移除失效節點前必須先將其關機，防止隔離 (Fencing) 失敗導致的腦裂 。
- `pmxcfs -l`: 在本地模式啟動叢集文件系統，用於救援無法正常加入通訊網環的節點 。

## 常見修復與維護模式
- **Web UI/API 無響應**: `systemctl restart pveproxy pvedaemon` 。
- **節點維護預備**: `ha-manager crm-command node-maintenance enable <nodename>` (自動遷移 HA 資源) 。
- **存儲 I/O 停頓**: 若為 NFS，檢查掛載選項是否為 `soft` 以防無限重試導致系統鎖死 。
- **網路配置變更應用**: `ifreload -a` (需安裝 `ifupdown2`) 。

## 效能基準指標 (pveperf)
- **REGEX/SECOND**: > 300,000 (Perl API 處理效能指標) 。
- **FSYNCS/SECOND**: > 2,000 為優質 SSD/RAID-BBU；< 200 表示存儲寫入效能可能嚴重拖慢 VM 。

## 常見問題排除技巧
- **高佇列延遲**: 檢查 `pvetop` 中的 `IOWait` 與 `Steal` 欄位，高值可能表示存儲或 CPU 競爭。
- **遷移失敗**: 使用 `qm migrate --online --with-local-disks <vmid> <target>` 並檢查來源與目的地的網路帶儲與存儲可用性。
- **備份卡住**: 檢查 `/var/log/pve/tasks/` 中的最新 UPID 日誌，常見原因是快照合併或存儲鎖定。
- **節點離線但未被移除**: 確認該節點的 `corosync` 與 `pve-cluster` 服務狀態，必要時使用 `pvecm delnode` 移除。
- **HA 資源無法啟動**: 檢查 `ha-manager status` 以及相應資源的系統日誌 (`journalctl -u pve-ha-lrm`)，常見錯誤為存儲路徑不可達或配置錯誤。
- **儲存池空間不足但警報未觸發**: 驗證 `pvesm` 配置中的警報閾值，以及使用 `pveperf` 檢查實際 I/O 延遲是否影響警示觸發。
- **叢集時間不同步**: 確認所有節點運行 `ntpd` 或 `chrony` 服務，時間差超過 0.5 秒可能導致 corosync 認證失效。
- **容器啟動失敗**: 檢查 `lxc-start -n <ctid> -F -l DEBUG` 的輸出，常見問題為掛載點權限或根檔案系統損毀。

Base directory for this skill: file:///root/.config/opencode/skills/pve-cluster-doctor
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.
Note: file list is sampled.

<skill_files>

</skill_files>