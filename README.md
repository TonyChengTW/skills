# OpenCode Skills Repository

專為 Linux 系統故障診斷、Proxmox VE 虛擬化環境維護，以及各類開發輔助任務設計的 OpenCode 技能庫。

## 目錄

- [技能概覽](#技能概覽)
- [快速開始](#快速開始)
- [技能詳述](#技能詳述)
  - [Linux Precision Triage](#linux-precision-triage)
  - [Proxmox Cluster Doctor](#proxmox-cluster-doctor)
  - [PVE UFW Manager](#pve-ufw-manager)
  - [Fun3sport WordPress Utils](#fun3sport-wordpress-utils)
  - [Humanizer (繁體中文)](#humanizer-繁體中文)
  - [Docusaurus Anchor Syntax](#docusaurus-anchor-syntax)
  - [Web Design Guidelines](#web-design-guidelines)
  - [OpenCode Server](#opencode-server)
- [Slash 命令參考](#slash-命令參考)
- [專案結構](#專案結構)
- [貢獻指南](#貢獻指南)
- [授權](#授權)

---

## 技能概覽

| 技能 | 描述 | 適用環境 |
|------|------|----------|
| `linux-precision-triage` | 使用最少 Token 消耗進行 Linux 系統故障診斷與修復 | Ubuntu 24.04+ |
| `pve-cluster-doctor` | Proxmox VE 虛擬化環境進階診斷與維護 | Proxmox VE 7.x/8.x |
| `pve-ufw-manager` | Proxmox VE 虛擬化環境 UFW 防火牆管理 | Proxmox VE / Debian |
| `fun3sport-wp-manager` | WordPress Docker 管理技能集（資料庫、容器、備份等） | Docker / WordPress |
| `humanizer-zh-TW` | 去除 AI 生成文字痕跡，使內容更自然 | 文字編輯 |
| `docusaurus-anchor-syntax` | Docusaurus MDX 錨點語法故障排除 | Docusaurus 專案 |
| `web-design-guidelines` | 審查 UI 代碼是否符合 Web Interface Guidelines | 前端開發 |
| `opencode-server` | 管理 OpenCode 伺服器環境（端口 4096） | OpenCode 部署 |

---

## 快速開始

### 前置需求

- [OpenCode](https://opencode.ai) 已安裝並運行
- 技能庫已放置於正確目錄：
  - 全域：`~/.config/opencode/skills/`
  - 專案：`.agents/skills/`

### 使用方式

1. 在對話中直接描述任務，OpenCode 會自動觸發對應技能
2. 或使用 Slash 命令快速呼叫特定功能（見下方命令參考）

---

## 技能詳述

### Linux Precision Triage

**目錄**: `linux-precision-triage/`

專注於用最精簡的命令定位 Linux (Ubuntu 24.04+) 問題，遵循 Token Saving Rules 以減少輸出量。

**核心準則**：
- 禁止使用無參數的 `dmesg` 或 `journalctl`
- 優先使用 `-br`（brief）、`-n`（行數）、`--no-pager`
- 執行命令時必須搭配 pipe（`grep`、`awk`）過濾關鍵錯誤

**診斷工作流**：

| 功能 | 命令 | 說明 |
|------|------|------|
| 系統健康快照 | `/linux-triage` | 系統負載、記憶體壓力、嚴重錯誤 |
| 網路堆疊掃描 | `/linux-net-audit` | 介面狀態、監聽埠、DNS 配置 |
| 儲存診斷 | `/linux-storage-audit` | 磁碟結構、ZFS 狀態、I/O 效能 |
| 叢集狀態檢查 | `/linux-cluster-audit` | 法定人數、HA 狀態（PVE 環境） |

**常用命令範例**：
```bash
# 系統健康
uptime && free -h
journalctl -p 3 -n 20 --no-pager

# 網路檢查
ip -br a
ss -tulpn

# 儲存檢查
lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT
zpool status -x
```

---

### Proxmox Cluster Doctor

**目錄**: `pve-cluster-doctor/`

專精於 Proxmox CLI 工具羣（`qm`、`pct`、`pvesm`、`pvecm`、`pveceph`）的進階診斷與維護。

**核心診斷工作流**：

| 功能 | 命令 | 說明 |
|------|------|------|
| VM/LXC 救援 | `/pve-vm-stuck` | 處理無法關閉、鎖定或遷移掛起的虛擬機 |
| 叢集健康檢查 | `/pve-health` | 法定人數、HA 狀態與系統效能快照 |
| 存儲後端診斷 | `/pve-storage-audit` | Ceph/ZFS/NFS 離線與延遲診斷 |
| 法定人數修復 | `/pve-quorum-fix` | 叢集緊急修復與節點強制移除 |

**常用命令範例**：
```bash
# 虛擬機狀態與解鎖
qm status <vmid>
qm unlock <vmid>

# 叢集狀態
pvecm status
ha-manager status

# 存儲狀態
pvesm status
pveceph status
```

**效能基準指標**（使用 `pveperf /`）：
- **FSYNCS/SECOND**: > 2000 為優質 SSD/RAID-BBU；< 200 表示存儲可能嚴重拖慢 VM
- **REGEX/SECOND**: > 300,000 為良好效能指標

---

### PVE UFW Manager

**目錄**: `pve-ufw-manager/`

提供 Proxmox VE 主機上 UFW 防火牆的自動化管理，具備安全、可 rollback 的規則管理框架。

**核心工具**：
- `ufw` - Ubuntu/Debian 防火牆管理工具
- `iptables` - 底層 netfilter 規則查詢
- `journalctl` - 系統日誌查閱

**工作流命令**：

| 功能 | 命令 | 說明 |
|------|------|------|
| 防火牆狀態 | `/pve-ufw-status` | 檢查防火牆狀態與規則 |
| 套用新規則 | `/pve-ufw-apply` | 套用新防火牆規則 |
| 預覽規則 | `/pve-ufw-dry-run` | 預覽即將套用的規則（不實際執行） |
| Rollback | `/pve-ufw-rollback` | 回滾到上一版本規則 |
| 查看日誌 | `/pve-ufw-logs` | 查看防火牆日誌 |

**腳本位置**：`scripts/ufw-hvm-manager.sh`

---

### Fun3sport WordPress Utils

**目錄**: `fun3sport-utils/`

完整的 WordPress Docker 部署維護技能集，提供 7 個專門模組，涵蓋 170+ 個函式。

**核心模組**：

| 模組 | 功能 | 主要函式 |
|------|------|----------|
| `db.py` | 資料庫管理 | `list_tables()`, `backup_database()`, `repair_table()` |
| `docker.py` | 容器生命週期 | `show_containers()`, `compose_up()`, `view_logs()` |
| `wordpress.py` | WordPress 管理 | `get_site_info()`, `update_plugin()`, `search_replace()` |
| `logs.py` | 日誌分析 | `analyze_wordpress_logs()`, `search_errors()` |
| `backup.py` | 備份還原 | `full_backup()`, `restore_database()`, `list_backups()` |
| `healthcheck.py` | 系統健康檢查 | `run_full_check()`, `check_disk_space()` |
| `main.py` | 統一 CLI 介面 | 互動式選單與命令列工具 |

**快速開始**：
```bash
# 啟動互動式選單
python3 /home/fun3sport/.agent/skill/main.py

# 常用命令
python3 /home/fun3sport/.agent/skill/main.py health
python3 /home/fun3sport/.agent/skill/main.py db --backup
python3 /home/fun3sport/.agent/skill/main.py wp --site-info
```

**配置說明**：
- 所有敏感資訊（資料庫密碼等）從 `.env` 檔案讀取
- `.env` 已加入 `.gitignore`，不會被提交到版本控制
- 參考 `.env.example` 進行配置

---

### Humanizer (繁體中文)

**目錄**: `humanizer-zh-TW/`

去除文字中的 AI 生成痕跡，使文字聽起來更自然、更像人類書寫。基於維基百科的「AI 寫作特徵」綜合指南。

**偵測並修復的 AI 寫作模式**：

| 類別 | 說明 |
|------|------|
| 誇大的象徵意義 | 過度強調意義、遺產和更廣泛的趨勢 |
| 宣傳性語言 | 「充滿活力的」、「豐富的」等誇張用語 |
| -ing 膚淺分析 | 以現在分詞結尾的虛假深度敘述 |
| 模糊歸因 | 「專家認為」、「觀察者指出」等無具體來源的主張 |
| AI 詞彙 | 「此外」、「至關重要」、「佈局」等高頻 AI 用語 |
| 否定式排比 | 「這不僅僅是...而是...」等過度使用結構 |
| 三段式法則 | 強行將想法分成三組 |
| 破折號過度使用 | 比人類更頻繁使用破折號 |
| 表情符號與格式 | 過度使用粗體、表情符號、彎引號 |

**使用場景**：
- 編輯或審閱 AI 生成的文字
- 去除文章的 AI 寫作痕跡
- 使內容更符合人類寫作風格

---

### Docusaurus Anchor Syntax

**目錄**: `docusaurus-anchor-syntax/`

解決 Docusaurus MDX 檔案中自定義錨點（anchor）無法被識別的問題。

**核心發現**：
> Docusaurus 的 `{#anchor-id}` 語法**僅適用於 h2-h6 標題層級**，**h1 標題會完全忽略此語法**。

| 標題層級 | `{#anchor}` 語法 | 是否有效 |
|---------|-------------------|----------|
| `# Heading` (h1) | `# Heading {#anchor}` | ❌ 無效 |
| `## Heading` (h2) | `## Heading {#anchor}` | ✅ 有效 |
| `### Heading` (h3) | `### Heading {#anchor}` | ✅ 有效 |

**解決方案**：
```markdown
# ❌ 錯誤：h1 無法使用自定義錨點
# 標題 {#my-anchor}

# ✅ 正確：改用 h2
## 標題 {#my-anchor}
```

**適用場景**：
- 解決 Docusaurus 構建時的 broken anchor 警告
- 修復 MDX 標題錨點問題
- 調試文件中的連結解析問題

---

### Web Design Guidelines

**目錄**: `web-design-guidelines/`

審查 UI 代碼是否符合 [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md) 規範。

**使用方式**：
1. 提供需要審查的檔案或 glob 模式
2. 技能會自動獲取最新的規範指南
3. 對代碼進行全面檢查
4. 以 `file:line` 格式輸出發現的問題

**觸發關鍵字**：
- "review my UI"
- "check accessibility"
- "audit design"
- "review UX"
- "check my site against best practices"

---

### OpenCode Server

**目錄**: `opencode-server/`

管理 OpenCode 伺服器環境，包含防火牆規則配置與伺服器啟動腳本。

**環境資訊**：
- **基礎目錄**：`/root/opencode-env/`
- **端口**：4096
- **關鍵檔案**：
  - `.env` - 包含 `OPENCODE_SERVER_PASSWORD` 與 `ALLOWED_IPS`
  - `secure_opencode.sh` - 防火牆設定 + 伺服器啟動腳本

**操作命令**：

| 操作 | 命令 |
|------|------|
| 啟動伺服器 | `./secure_opencode.sh` |
| 檢查狀態 | `pgrep -f "opencode serve"` |
| 檢查端口 | `ss -tlnp \| grep 4096` |
| 檢查防火牆 | `sudo iptables -L INPUT -n \| grep 4096` |
| 停止伺服器 | `pkill -f "opencode serve"` |

**安全注意事項**：
- IP 白名單：僅 `ALLOWED_IPS` 中的 IP 可以連接
- 預設拒絕：所有其他 IP 會被 iptables DROP 規則阻擋
- 密碼：透過 `.env` 中的 `OPENCODE_SERVER_PASSWORD` 設定

---

## Slash 命令參考

### Linux 系統診斷

| 命令 | 技能 | 說明 |
|------|------|------|
| `/linux-triage` | linux-precision-triage | 系統健康快照（負載、記憶體、錯誤日誌） |
| `/linux-net-audit` | linux-precision-triage | 精簡化網路堆疊掃描 |
| `/linux-storage-audit` | linux-precision-triage | 快速儲存池與效能診斷 |
| `/linux-cluster-audit` | linux-precision-triage | 叢集法定人數與 HA 狀態檢查 |

### Proxmox 叢集管理

| 命令 | 技能 | 說明 |
|------|------|------|
| `/pve-vm-stuck` | pve-cluster-doctor | 處理無法關閉、鎖定或遷移掛起的 VM/LXC |
| `/pve-health` | pve-cluster-doctor | 叢集法定人數、HA 狀態與系統效能快照 |
| `/pve-storage-audit` | pve-cluster-doctor | 存儲後端 (Ceph/ZFS/NFS) 離線與延遲診斷 |
| `/pve-quorum-fix` | pve-cluster-doctor | 叢集法定人數緊急修復與節點強制移除 |

### Proxmox 防火牆管理

| 命令 | 技能 | 說明 |
|------|------|------|
| `/pve-ufw-status` | pve-ufw-manager | 檢查防火牆狀態 |
| `/pve-ufw-apply` | pve-ufw-manager | 套用新防火牆規則 |
| `/pve-ufw-dry-run` | pve-ufw-manager | 預覽即將套用的規則 |
| `/pve-ufw-rollback` | pve-ufw-manager | Rollback 到上一版本 |
| `/pve-ufw-logs` | pve-ufw-manager | 查看防火牆日誌 |

---

## 專案結構

```
skills/
├── AGENTS.md                      # Agent 使用指南
├── README.md                      # 本文件
├── linux-precision-triage/         # Linux 系統診斷技能
│   └── SKILL.md
├── pve-cluster-doctor/            # Proxmox 叢集醫生技能
│   └── SKILL.md
├── pve-ufw-manager/               # Proxmox UFW 防火牆管理
│   ├── SKILL.md
│   ├── scripts/
│   │   └── ufw-hvm-manager.sh
│   └── reference/
│       └── ufw-ports.md
├── fun3sport-utils/               # WordPress Docker 管理技能集
│   ├── SKILL.md
│   ├── main.py                    # 統一 CLI 介面
│   ├── db.py                      # 資料庫模組
│   ├── docker.py                  # Docker 模組
│   ├── wordpress.py               # WordPress 模組
│   ├── logs.py                    # 日誌分析模組
│   ├── backup.py                  # 備份還原模組
│   ├── healthcheck.py             # 健康檢查模組
│   └── .env.example               # 環境變數範本
├── humanizer-zh-TW/               # 去除 AI 寫作痕跡技能
│   └── SKILL.md
├── docusaurus-anchor-syntax/      # Docusaurus 錨點語法指南
│   └── SKILL.md
├── web-design-guidelines/         # Web 設計規範審查
│   └── SKILL.md
└── opencode-server/               # OpenCode 伺服器管理
    ├── SKILL.md
    ├── .env
    └── secure_opencode.sh
```

---

## 貢獻指南

### 新增技能

1. 建立新目錄：`mkdir new-skill-name`
2. 建立 `SKILL.md` 檔案，包含 YAML frontmatter：
   ```yaml
   ---
   name: new-skill-name
   description: 技能簡述
   commands:
     - /command-name: 命令說明
   ---
   ```
3. 撰寫技能內容（使用 Markdown 格式）
4. 更新本 `README.md` 與 `AGENTS.md`

### 技能開發建議

- 遵循現有技能的結構與風格
- 提供清晰的使用範例
- 包含故障排除指南
- 標註適用的環境與依賴工具

---

## 授權

- `fun3sport-utils`: MIT License
- 其他技能：請參閱各技能目錄中的授權資訊

---

## 相關連結

- [OpenCode 官方網站](https://opencode.ai)
- [OpenCode GitHub](https://github.com/anomalyco/opencode)
- [Proxmox VE 文件](https://pve.proxmox.com/wiki/Main_Page)
- [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
