---
name: fun3sport-wp-manager
description: Comprehensive WordPress Docker management skill set for fun3sport project. Provides database operations, Docker container management, WordPress administration, log analysis, backup/restore, and health monitoring capabilities.
license: MIT
---

# Fun3sport WordPress Docker Management Skill Set

## Overview

A complete skill set for maintaining, debugging, and operating the fun3sport WordPress Docker deployment. This skill set provides 7 specialized modules covering all aspects of WordPress Docker operations.

**Key Capabilities:**
- 🗄️ Database management (MariaDB operations, backups, queries)
- 🐳 Docker container lifecycle management
- 🌐 WordPress administration via WP-CLI
- 📜 Log analysis and error tracking
- 💾 Automated backup and restore
- 🏥 System health monitoring and diagnostics

---

# Quick Start

## Launch Interactive Menu

```bash
python3 /home/fun3sport/.agent/skill/main.py
```

## Common Commands

```bash
# Container Management
python3 /home/fun3sport/.agent/skill/main.py docker --status
python3 /home/fun3sport/.agent/skill/main.py docker --up
python3 /home/fun3sport/.agent/skill/main.py docker --down

# Database Operations
python3 /home/fun3sport/.agent/skill/main.py db --list-tables
python3 /home/fun3sport/.agent/skill/main.py db --backup

# WordPress Management
python3 /home/fun3sport/.agent/skill/main.py wp --site-info
python3 /home/fun3sport/.agent/skill/main.py wp --plugins

# Backup & Health
python3 /home/fun3sport/.agent/skill/main.py backup --full
python3 /home/fun3sport/.agent/skill/main.py health
```

---

# Process

## Phase 1: System Health Check

Before performing any maintenance, run a comprehensive health check:

```python
from skill.healthcheck import run_full_check, print_health_report

results = run_full_check()
print_health_report(results)
```

This validates:
- Docker daemon status
- Container states (WordPress & Database)
- Database connectivity
- Website accessibility
- Disk and memory usage
- File integrity

## Phase 2: Daily Operations

### 2.1 Check Container Status

```python
from skill.docker import show_containers, show_stats

show_containers()  # Display running containers
show_stats()       # Show resource usage
```

### 2.2 View Logs

```python
from skill.logs import analyze_wordpress_logs, search_errors

# Analyze recent logs
result = analyze_wordpress_logs(lines=100)

# Search for specific errors
errors = search_errors("database")
```

### 2.3 Database Inspection

```python
from skill.db import list_tables, get_table_structure

tables = list_tables()
for table in tables:
    structure = get_table_structure(table)
    print(f"{table}: {len(structure['columns'])} columns")
```

## Phase 3: Maintenance Tasks

### 3.1 WordPress Updates

```python
from skill.wordpress import update_core, update_plugin, update_theme

# Update WordPress core
update_core()

# Update all plugins
update_plugin()

# Update all themes
update_theme()
```

### 3.2 Backup Operations

```python
from skill.backup import full_backup, backup_database, backup_files

# Complete backup (database + files)
full_backup()

# Individual component backup
backup_database()
backup_files()
```

### 3.3 Performance Optimization

```python
from skill.wordpress import flush_cache, rewrite_flush
from skill.db import optimize_table

# Clear WordPress caches
flush_cache()

# Optimize database tables
optimize_table("wp_posts")
optimize_table("wp_postmeta")
```

## Phase 4: Troubleshooting

### 4.1 Container Issues

```python
from skill.docker import view_logs, exec_interactive

# Check container logs
view_logs("fun3sport_wp", lines=50)

# Enter container shell
exec_interactive("fun3sport_wp", "bash")
```

### 4.2 Database Issues

```python
from skill.db import check_db_health, repair_table

# Check database health
health = check_db_health()

# Repair corrupted table
repair_table("wp_posts")
```

### 4.3 WordPress Issues

```python
from skill.wordpress import check_core, search_replace

# Verify core file integrity
check_core()

# Fix URL issues
search_replace("old-domain.com", "new-domain.com", dry_run=False)
```

---

# Skill Modules Reference

## 🗄️ Database Skill (db.py)

**Purpose:** MariaDB database operations and management

**Key Functions:**

| Function | Description |
|----------|-------------|
| `run_mysql_command(sql)` | Execute SQL commands via docker exec |
| `run_mysql_interactive()` | Launch interactive MySQL shell |
| `list_tables()` | List all database tables |
| `get_table_structure(table)` | Get table column definitions |
| `sample_table_data(table, limit)` | Retrieve sample records |
| `backup_database()` | Create database backup |
| `restore_database(file)` | Restore from backup file |
| `get_wp_options()` | Read WordPress configuration options |
| `check_db_health()` | Validate database health |
| `repair_table(table)` | Repair corrupted tables |
| `optimize_table(table)` | Optimize table performance |

**Configuration:**

資料庫憑證從 `.env` 檔案讀取（不硬編碼在程式碼中）：

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 從 .env 檔案載入環境變數

DB_CONFIG = {
    "database": os.getenv("DB_NAME", "wordpress_db"),
    "user": os.getenv("DB_USER", "wp_user"),
    "password": os.getenv("DB_PASSWORD"),  # 從 .env 讀取
    "root_password": os.getenv("DB_ROOT_PASSWORD"),  # 從 .env 讀取
}
```

**注意：** 密碼等機敏資訊必須在 `.env` 檔案中配置，不應硬編碼在程式碼中。

**Example:**
```python
from skill.db import list_tables, backup_database

# List all tables with row counts
tables = list_tables()
for table in tables:
    count = get_table_count(table)
    print(f"{table}: {count} rows")

# Create backup
backup_file = backup_database()
```

---

## 🐳 Docker Skill (docker.py)

**Purpose:** Container lifecycle and orchestration management

**Key Functions:**

| Function | Description |
|----------|-------------|
| `show_containers()` | Display container status overview |
| `list_containers()` | List all containers with details |
| `container_running(name)` | Check if container is running |
| `start_container(name)` | Start a stopped container |
| `stop_container(name)` | Stop a running container |
| `restart_container(name)` | Restart a container |
| `view_logs(name, lines)` | Retrieve container logs |
| `exec_interactive(name, shell)` | Enter container shell |
| `compose_up()` | Start all services |
| `compose_down(volumes)` | Stop and optionally remove volumes |
| `compose_restart(service)` | Restart services |
| `show_networks()` | Display network information |
| `show_stats()` | Show resource usage |
| `cleanup_system()` | Remove unused Docker resources |
| `health_check()` | Validate Docker environment |

**Configuration:**
```python
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
NETWORK_NAME = "fun3sport_net"
```

**Example:**
```python
from skill.docker import compose_up, view_logs, show_stats

# Start all services
compose_up()

# Monitor logs
view_logs("fun3sport_wp", follow=True)

# Check resource usage
show_stats()
```

---

## 🌐 WordPress Skill (wordpress.py)

**Purpose:** WordPress site administration via WP-CLI

**Key Functions:**

| Function | Description |
|----------|-------------|
| `get_site_info()` | Retrieve site configuration |
| `show_site_info()` | Display site information |
| `list_plugins()` | List installed plugins |
| `activate_plugin(name)` | Activate a plugin |
| `deactivate_plugin(name)` | Deactivate a plugin |
| `install_plugin(name)` | Install from WordPress.org |
| `update_plugin(name)` | Update plugin to latest |
| `list_themes()` | List installed themes |
| `activate_theme(name)` | Switch active theme |
| `list_users()` | List WordPress users |
| `create_user(user, email, role)` | Create new user |
| `update_user_password(id, pwd)` | Change user password |
| `list_posts()` | List recent posts |
| `search_replace(old, new)` | Replace text in database |
| `flush_cache()` | Clear WordPress caches |
| `update_core()` | Update WordPress version |
| `check_core()` | Verify file integrity |
| `export_database()` | Export via WP-CLI |

**Configuration:**
```python
CONTAINER_WP = "fun3sport_wp"
WP_CLI_PATH = "/var/www/html/wp-cli.phar"
```

**Example:**
```python
from skill.wordpress import get_site_info, update_plugin, flush_cache

# Check site configuration
info = get_site_info()
print(f"WordPress {info['version']} at {info['url']}")

# Update all plugins
update_plugin()

# Clear caches
flush_cache()
```

---

## 📜 Logs Skill (logs.py)

**Purpose:** Log analysis and error tracking

**Key Functions:**

| Function | Description |
|----------|-------------|
| `get_docker_logs(container, lines)` | Retrieve container logs |
| `analyze_wordpress_logs(lines)` | Analyze WordPress error patterns |
| `analyze_db_logs(lines)` | Analyze database logs |
| `search_errors(keyword)` | Search for specific errors |
| `get_error_summary(hours)` | Generate error statistics |
| `follow_logs(container)` | Real-time log streaming |
| `export_logs(path)` | Save logs to file |
| `analyze_log_patterns()` | Identify request patterns |

**Error Patterns Detected:**
- PHP Fatal/Warnings/Notices
- MySQL connection errors
- WordPress database errors
- HTTP 404/500 errors
- Slow queries

**Example:**
```python
from skill.logs import search_errors, get_error_summary

# Search for fatal errors
fatal_errors = search_errors("fatal")

# Get 24-hour summary
summary = get_error_summary(hours=24)
for error_type, count in summary.items():
    print(f"{error_type}: {count}")
```

---

## 💾 Backup Skill (backup.py)

**Purpose:** Comprehensive backup and restore operations

**Key Functions:**

| Function | Description |
|----------|-------------|
| `backup_database()` | Export database to .sql.gz |
| `backup_files()` | Archive wp_data directory |
| `full_backup()` | Complete site backup |
| `restore_database(file)` | Import database backup |
| `restore_files(file)` | Restore from archive |
| `list_backups()` | List available backups |
| `cleanup_old_backups(days)` | Remove old backups |
| `get_backup_size()` | Calculate storage usage |
| `schedule_backup()` | Generate cron instructions |

**Backup Structure:**
```
/home/fun3sport/backups/
├── db_backup_20260423_120000.sql.gz
├── files_backup_20260423_120000.tar.gz
└── full_backup_20260423_120000.tar.gz
```

**Example:**
```python
from skill.backup import full_backup, list_backups, cleanup_old_backups

# Create complete backup
archive = full_backup()

# List all backups
backups = list_backups()

# Clean old backups
cleanup_old_backups(keep_days=30)
```

---

## 🏥 Health Check Skill (healthcheck.py)

**Purpose:** System-wide health diagnostics

**Key Functions:**

| Function | Description |
|----------|-------------|
| `run_full_check()` | Execute all health checks |
| `check_docker_daemon()` | Verify Docker service |
| `check_container_status(name)` | Check container state |
| `check_database_connection()` | Test DB connectivity |
| `check_wordpress_response()` | Verify site accessibility |
| `check_disk_space()` | Monitor disk usage |
| `check_memory()` | Check memory utilization |
| `check_wordpress_files()` | Validate file integrity |
| `get_system_info()` | Collect system metadata |
| `print_health_report(results)` | Display formatted report |
| `save_health_report(results, path)` | Save report to file |

**Checks Performed:**
1. Docker daemon running
2. WordPress container status
3. Database container status
4. WordPress site response
5. Database connectivity
6. Disk space availability
7. Memory usage
8. Network connectivity
9. WordPress file integrity
10. Database size
11. WP configuration validity
12. Backup directory status
13. Log file accessibility

**Example:**
```python
from skill.healthcheck import run_full_check, print_health_report, save_health_report

# Run diagnostics
results = run_full_check()

# Display report
print_health_report(results)

# Save to file
save_health_report(results, "/home/fun3sport/backups/health_report.txt")
```

---

# Main Entry Point

## Module Structure

```python
# skill/main.py - Unified CLI interface

import db
import docker
import wordpress
import logs
import backup
import healthcheck

def main_cli():
    """Interactive menu system"""
    pass

def run_health_check():
    """Quick health check command"""
    pass

def db_command(args):
    """Database subcommand handler"""
    pass

def docker_command(args):
    """Docker subcommand handler"""
    pass

def wp_command(args):
    """WordPress subcommand handler"""
    pass

def logs_command(args):
    """Logs subcommand handler"""
    pass

def backup_command(args):
    """Backup subcommand handler"""
    pass
```

## CLI Arguments

```bash
# Interactive mode
python3 skill/main.py
python3 skill/main.py cli

# Direct commands
python3 skill/main.py db --list-tables
python3 skill/main.py docker --status
python3 skill/main.py wp --site-info
python3 skill/main.py logs --errors
python3 skill/main.py backup --full
python3 skill/main.py health
```

---

# Configuration

## Environment Configuration (.env)

**重要：** 所有機敏資訊（資料庫密碼、API 金鑰等）都已從程式碼抽離，改為從 `.env` 檔案讀取。這樣可以安全地將程式碼推送到 GitHub，而不洩露敏感資訊。

**資料庫憑證配置：** 本技能不包含資料庫密碼等機敏資訊。所有憑證都儲存在 `.env` 檔案中，請參考下方的 `.env` 配置說明。

### Step 1: 複製範本檔案

```bash
cd /home/fun3sport/.agent/fun3sport-utils
cp .env.example .env
```

### Step 2: 編輯 .env 檔案

使用文字編輯器開啟 `.env` 並填入真實的密碼：

```bash
nano .env
```

`.env` 檔案內容範例：

```bash
# =============================================================================
# DATABASE CREDENTIALS (REQUIRED)
# =============================================================================

# WordPress 資料庫使用者密碼（請替換為實際密碼）
DB_PASSWORD=your_secure_password_here

# MariaDB root 密碼（用於管理任務，請替換為實際密碼）
DB_ROOT_PASSWORD=your_secure_root_password_here

# =============================================================================
# WORDPRESS SETTINGS (OPTIONAL)
# =============================================================================

# WordPress 網站 URL
WP_URL=http://localhost:8333

# WordPress 連接埠
WP_PORT=8333

# =============================================================================
# PROJECT PATHS (OPTIONAL)
# =============================================================================

# 專案基礎目錄
PROJECT_DIR=/home/fun3sport

# =============================================================================
# BACKUP SETTINGS (OPTIONAL)
# =============================================================================

# 預設備份保留天數
BACKUP_RETENTION_DAYS=30

# 備份目錄（相對於 PROJECT_DIR）
BACKUP_DIR=backups
```

### Step 3: 確保 .env 不被提交

`.env` 檔案已加入 `.gitignore`（請確認專案根目錄的 `.gitignore` 包含以下內容）：

```gitignore
# Environment variables
.env
.env.local
.env.*.local
```

---

## Environment Constants

所有模組共享以下設定常數。敏感資訊從環境變數動態讀取，非敏感資訊直接硬編碼：

```python
from pathlib import Path
import os

# 載入 .env 檔案
def load_env_file():
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = value

load_env_file()

# =============================================================================
# NON-SENSITIVE CONFIGURATION (Safe to hardcode)
# =============================================================================

# 專案路徑
PROJECT_DIR = Path(os.getenv("PROJECT_DIR", "/home/fun3sport"))
WP_DATA_DIR = PROJECT_DIR / "wp_data"
DB_DATA_DIR = PROJECT_DIR / "db_data"
BACKUP_DIR = PROJECT_DIR / os.getenv("BACKUP_DIR", "backups")

# 容器名稱（非敏感資訊）
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
NETWORK_NAME = "fun3sport_net"

# =============================================================================
# SENSITIVE CONFIGURATION (Loaded from .env)
# =============================================================================

# 資料庫憑證（從環境變數讀取）
DB_CONFIG = {
    "host": "db",
    "port": 3306,
    "database": "wordpress_db",
    "user": "wp_user",
    "password": os.getenv("DB_PASSWORD", "CHANGE_ME"),
    "root_password": os.getenv("DB_ROOT_PASSWORD", "CHANGE_ME"),
}

# WordPress 設定
WP_CONFIG = {
    "url": os.getenv("WP_URL", "http://localhost:8333"),
    "port": int(os.getenv("WP_PORT", "8333")),
    "wp_data": PROJECT_DIR / "wp_data",
    "db_data": PROJECT_DIR / "db_data",
}

# 備份設定
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
```

---

## Import Configuration in Skill Modules

在各個技能模組中，統一從 `__init__.py` 導入設定：

```python
# 在所有技能模組頂部加入：
from . import (
    PROJECT_DIR, CONTAINER_WP, CONTAINER_DB, DB_CONFIG, WP_CONFIG,
    BACKUP_DIR, BACKUP_RETENTION_DAYS, check_sensitive_config
)

# 使用設定
print(f"Database user: {DB_CONFIG['user']}")
print(f"Database password: {DB_CONFIG['password']}")  # 從 .env 讀取
print(f"WordPress URL: {WP_CONFIG['url']}")
```

---

## Security Best Practices

### ✅ 正確做法

1. **提交 `.env.example`** 到 GitHub - 這是安全的範本檔案
2. **絕不提交 `.env`** - 包含真實密碼
3. **使用強密碼** - 生產環境使用複雜密碼
4. **限制檔案權限** - `.env` 設定為 600 權限：
   ```bash
   chmod 600 /home/fun3sport/.agent/skill/.env
   ```

### ❌ 錯誤做法

- 在程式碼中直接寫入密碼
- 將 `.env` 提交到版本控制
- 在 Log 中輸出密碼
- 分享包含真實密碼的檔案

---

## Configuration Validation

啟動時自動檢查敏感設定是否正確：

```python
from skill import check_sensitive_config

# 檢查設定
if not check_sensitive_config():
    print("設定檢查失敗，請確認 .env 檔案")
    exit(1)
```

這會輸出：
- 如果 `DB_PASSWORD` 未設定 → "警告: DB_PASSWORD 未設定，請檢查 .env 檔案"
- 如果 `DB_ROOT_PASSWORD` 未設定 → "警告: DB_ROOT_PASSWORD 未設定，請檢查 .env 檔案"
- 如果都正確 → 無警告，返回 True

---

# Common Workflows

## Daily Maintenance

```python
from skill.healthcheck import run_full_check, print_health_report
from skill.backup import full_backup
from skill.logs import show_error_summary

# 1. Health check
results = run_full_check()
print_health_report(results)

# 2. Backup
full_backup()

# 3. Check for errors
show_error_summary()
```

## Migration Process

```python
from skill.backup import backup_database, backup_files
from skill.wordpress import search_replace

# 1. Backup everything
db_backup = backup_database()
files_backup = backup_files()

# 2. Update URLs
search_replace("old-domain.com", "new-domain.com", dry_run=False)

# 3. Verify
from skill.healthcheck import check_wordpress_response
status, msg = check_wordpress_response()
```

## Troubleshooting

```python
from skill.healthcheck import run_full_check
from skill.logs import search_errors
from skill.docker import view_logs

# 1. Full diagnostic
results = run_full_check()

# 2. Check recent errors
errors = search_errors()

# 3. View container logs
logs = view_logs("fun3sport_wp", lines=200)
```

---

# Error Handling

All functions follow consistent error handling patterns:

```python
def example_function() -> Union[bool, str]:
    """Return True on success, error message on failure"""
    try:
        # Operation code
        return True
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.stderr}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

Health check functions return tuples:

```python
def check_something() -> Tuple[bool, str]:
    """Return (status, message)"""
    if healthy:
        return True, "Component is healthy"
    else:
        return False, "Error description"
```

---

# Best Practices

## 1. Always Check Health First

```python
from skill.healthcheck import run_full_check

results = run_full_check()
if not all(status for status, _ in results.values()):
    print("System not healthy, aborting operation")
    exit(1)
```

## 2. Backup Before Major Changes

```python
from skill.backup import full_backup

backup = full_backup()
if not backup:
    print("Backup failed, aborting")
    exit(1)
```

## 3. Use Dry Run for Destructive Operations

```python
from skill.wordpress import search_replace

# Preview first
output = search_replace("old", "new", dry_run=True)
print(output)

# Confirm then execute
confirm = input("Proceed? (yes/no): ")
if confirm == "yes":
    search_replace("old", "new", dry_run=False)
```

## 4. Handle Interactive Prompts

```python
from skill.docker import compose_down

# For non-interactive usage
compose_down(volumes=False)  # Don't prompt
```

---

# Troubleshooting

## Container Won't Start

```bash
# Check Docker daemon
python3 skill/main.py health

# View detailed logs
python3 skill/main.py docker --logs --follow

# Check system resources
docker system df
```

## Database Connection Failed

```bash
# Verify container is running
docker ps | grep fun3sport_db

# Check database logs
python3 skill/main.py logs --db

# Test connection manually
python3 skill/main.py db --interactive
```

## WordPress Errors

```bash
# Check for PHP errors
python3 skill/main.py logs --errors

# Verify core files
python3 skill/main.py wp --site-info

# Check file permissions
python3 skill/main.py docker --shell -s fun3sport_wp
# Then: ls -la /var/www/html
```

---

# API Reference

## Direct Module Import

```python
import sys
sys.path.insert(0, "/home/fun3sport/.agent/skill")

from db import list_tables, backup_database
from docker import compose_up, show_containers
from wordpress import get_site_info, update_plugin
from logs import search_errors
from backup import full_backup
from healthcheck import run_full_check
```

## Function Signatures

See individual module files for complete function signatures and documentation.

---

# Version History

## v1.0.0 (2026-04-23)
- Initial release
- 7 skill modules with 170+ functions
- Interactive CLI and command-line interface
- Comprehensive health checking
- Automated backup/restore
- Full WordPress management via WP-CLI

---

# Support

For issues or questions:
1. Run `python3 skill/main.py health` to diagnose
2. Check logs with `python3 skill/main.py logs --errors`
3. Review documentation in `/home/fun3sport/.agent/skill/README.md`

---

**License:** MIT  
**Author:** fun3sport  
**Last Updated:** 2026-04-23
