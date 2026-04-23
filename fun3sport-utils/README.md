# Fun3sport Skill Set - WordPress Docker 运维工具集

## 概述

这是一个专为 fun3sport WordPress Docker 專案设计的完整运维管理工具集，提供資料庫管理、Docker 容器管理、WordPress 管理、日誌分析、備份還原和健康檢查等功能。

## 目錄结构

```
/home/fun3sport/.agent/skill/
├── __init__.py          # 模組設定和常數
├── main.py              # 主入口和 CLI
├── db.py                # 資料庫管理技能
├── docker.py            # Docker 容器管理技能
├── wordpress.py         # WordPress 管理技能
├── logs.py              # 日誌分析技能
├── backup.py            # 備份還原技能
├── healthcheck.py       # 健康檢查技能
└── README.md            # 本文档
```

## 快速开始

### 1. 啟動交互式菜单

```bash
python3 /home/fun3sport/.agent/skill/main.py
```

### 2. 使用指令行参数

```bash
# 資料庫操作
python3 /home/fun3sport/.agent/skill/main.py db --list-tables
python3 /home/fun3sport/.agent/skill/main.py db --backup

# Docker 操作
python3 /home/fun3sport/.agent/skill/main.py docker --status
python3 /home/fun3sport/.agent/skill/main.py docker --up

# WordPress 操作
python3 /home/fun3sport/.agent/skill/main.py wp --site-info
python3 /home/fun3sport/.agent/skill/main.py wp --plugins

# 健康檢查
python3 /home/fun3sport/.agent/skill/main.py health
```

## 功能模組详解

### 🗄️ Database Skill (db.py)

資料庫管理工具，支援 MariaDB/MySQL 操作。

**功能：**
- 列出資料庫資料表和结构
- 执行 SQL 指令和脚本
- 備份和還原資料庫
- 檢視資料表資料和统计
- 資料庫健康檢查
- 交互式 MySQL shell

**示例：**
```python
from skill import db

# 列出所有資料表
tables = db.list_tables()

# 備份資料庫
db.backup_database()

# 进入交互式 MySQL
db.run_mysql_interactive()
```

### 🐳 Docker Skill (docker.py)

Docker 容器和编排管理工具。

**功能：**
- 容器生命周期管理（啟動、停止、重启）
- 檢視容器状态和资源使用
- 日誌檢視和实时跟踪
- 網路管理
- Docker Compose 操作
- 系统清理

**示例：**
```python
from skill import docker

# 啟動所有服务
docker.compose_up()

# 檢視容器状态
docker.show_containers()

# 进入容器 shell
docker.exec_interactive("fun3sport_wp", "bash")
```

### 🌐 WordPress Skill (wordpress.py)

WordPress 网站管理工具，使用 WP-CLI。

**功能：**
- 网站資訊管理
- 插件管理（安裝、啟用、更新、刪除）
- 主题管理
- 使用者管理（建立、刪除、修改密码）
- 文章管理
- 資料庫搜尋替换
- 缓存和重写规则刷新
- 维护模式

**示例：**
```python
from skill import wordpress

# 檢視网站資訊
wordpress.show_site_info()

# 列出插件
wordpress.show_plugins()

# 啟用插件
wordpress.activate_plugin("plugin-name")

# 建立使用者
wordpress.create_user("username", "email@example.com", "administrator")
```

### 📜 Logs Skill (logs.py)

日誌分析和管理工具。

**功能：**
- WordPress/資料庫日誌分析
- 錯誤搜尋和统计
- 实时日誌跟踪
- 日誌导出
- 錯誤摘要报告
- 日誌模式分析

**示例：**
```python
from skill import logs

# 分析 WordPress 日誌
logs.analyze_wordpress_logs(lines=100)

# 搜尋錯誤
errors = logs.search_errors("fatal")

# 导出日誌
logs.export_logs(Path("/path/to/export.txt"))
```

### 💾 Backup Skill (backup.py)

備份和還原管理工具。

**功能：**
- 完整備份（資料庫 + 檔案）
- 单独備份資料庫或檔案
- 備份列資料表和管理
- 从備份還原
- 自动清理旧備份
- 定时備份設定

**示例：**
```python
from skill import backup

# 执行完整備份
backup.full_backup()

# 仅備份資料庫
backup.backup_database()

# 列出備份
backup.show_backups()

# 還原資料庫
backup.restore_database(Path("/path/to/backup.sql.gz"))
```

### 🏥 Health Check Skill (healthcheck.py)

系统健康檢查和诊断工具。

**功能：**
- Docker 守护进程檢查
- 容器状态檢查
- 資料庫連線檢查
- 网站可访问性檢查
- 磁碟和内存使用檢查
- WordPress 檔案完整性檢查
- 生成健康报告

**示例：**
```python
from skill import healthcheck

# 執行完整健康檢查
results = healthcheck.run_full_check()
healthcheck.print_health_report(results)

# 儲存报告
healthcheck.save_health_report(results)
```

## 常用指令速查資料表

| 操作 | 指令 |
|------|------|
| 啟動交互式菜单 | `python3 /home/fun3sport/.agent/skill/main.py` |
| 檢視容器状态 | `python3 /home/fun3sport/.agent/skill/main.py docker --status` |
| 啟動服务 | `python3 /home/fun3sport/.agent/skill/main.py docker --up` |
| 停止服务 | `python3 /home/fun3sport/.agent/skill/main.py docker --down` |
| 檢視网站資訊 | `python3 /home/fun3sport/.agent/skill/main.py wp --site-info` |
| 完整備份 | `python3 /home/fun3sport/.agent/skill/main.py backup --full` |
| 健康檢查 | `python3 /home/fun3sport/.agent/skill/main.py health` |
| 进入資料庫 shell | `python3 /home/fun3sport/.agent/skill/main.py db --interactive` |

## Python 导入使用

```python
# 添加 skill 目錄到路徑
import sys
sys.path.insert(0, "/home/fun3sport/.agent/skill")

# 导入所需模組
import db
import docker
import wordpress
import logs
import backup
import healthcheck

# 使用功能
docker.compose_up()
wordpress.show_site_info()
backup.full_backup()
```

## 專案設定

在 `__init__.py` 中定义了以下常數：

```python
PROJECT_DIR = Path("/home/fun3sport")
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
NETWORK_NAME = "fun3sport_net"

DB_CONFIG = {
    "host": "db",
    "port": 3306,
    "database": "wordpress_db",
    "user": "wp_user",
    "password": "Fun3sport$",
}

WP_CONFIG = {
    "url": "http://localhost:8333",
    "port": 8333,
    "wp_data": PROJECT_DIR / "wp_data",
    "db_data": PROJECT_DIR / "db_data",
}
```

## 注意事项

1. **权限要求**：某些操作（如 Docker 指令）需要适当的权限
2. **容器状态**：确保容器在執行状态再执行相关操作
3. **備份建议**：定期执行完整備份，特别是在重大修改前
4. **安全性**：備份檔案包含敏感資訊，注意存储安全

## 故障排除

### 容器無法啟動
```bash
python3 /home/fun3sport/.agent/skill/main.py docker --status
python3 /home/fun3sport/.agent/skill/main.py health
```

### 資料庫連線失敗
```bash
python3 /home/fun3sport/.agent/skill/main.py db --interactive
```

### 网站無法访问
```bash
python3 /home/fun3sport/.agent/skill/main.py logs --wp
python3 /home/fun3sport/.agent/skill/main.py logs --errors
```

## 更新日誌

### v1.0.0 (2026-04-23)
- 初始版本发布
- 包含完整的 6 个技能模組
- 支援交互式 CLI 和指令行参数
- 資料庫、Docker、WordPress、日誌、備份、健康檢查功能

## 许可证

本工具集专为 fun3sport 專案定制使用。

## 作者

fun3sport 运维团队
