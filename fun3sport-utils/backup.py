#!/usr/bin/env python3
"""
Backup Skill - 備份與還原管理工具集
提供完整的資料庫、檔案、網站全量備份與還原功能
"""

import subprocess
import tarfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# 從 __init__.py 導入配置
from . import (
    PROJECT_DIR, CONTAINER_WP, CONTAINER_DB, DB_CONFIG,
    BACKUP_DIR, BACKUP_RETENTION_DAYS, check_sensitive_config
)

WP_DATA_DIR = PROJECT_DIR / "wp_data"
DB_DATA_DIR = PROJECT_DIR / "db_data"

# 確保備份目錄存在
BACKUP_DIR.mkdir(exist_ok=True)


def run_command(cmd: List[str]) -> tuple:
    """執行 shell 指令"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def backup_database(output_path: Optional[Path] = None) -> Optional[Path]:
    """備份資料庫"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        output_path = BACKUP_DIR / f"db_backup_{timestamp}.sql"
    
    print(f"💾 備份資料庫...")
    print(f"   目標: {output_path}")
    
    # 使用 docker exec mysqldump
    # 從 DB_CONFIG 讀取 root 密碼
    root_password = DB_CONFIG.get("root_password", "")
    cmd = [
        "docker", "exec", CONTAINER_DB,
        "mysqldump", "-u", "root",
        f"-p{root_password}",
        "--databases", "wordpress_db",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--hex-blob"
    ]
    
    try:
        with open(output_path, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        # 壓縮
        compressed_path = Path(str(output_path) + ".gz")
        with open(output_path, 'rb') as f_in:
            import gzip
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        output_path.unlink()  # 刪除原始 SQL
        
        size_mb = compressed_path.stat().st_size / 1024 / 1024
        print(f"✅ 資料庫備份完成: {compressed_path}")
        print(f"   大小: {size_mb:.2f} MB")
        
        return compressed_path
    
    except subprocess.CalledProcessError as e:
        print(f"❌ 備份失敗: {e}")
        return None


def backup_files(output_path: Optional[Path] = None) -> Optional[Path]:
    """備份 WordPress 檔案"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        output_path = BACKUP_DIR / f"files_backup_{timestamp}.tar.gz"
    
    print(f"💾 備份 WordPress 檔案...")
    print(f"   目標: {output_path}")
    print(f"   源目錄: {WP_DATA_DIR}")
    
    try:
        # 建立 tar.gz 歸檔
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(WP_DATA_DIR, arcname="wp_data")
        
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"✅ 檔案備份完成: {output_path}")
        print(f"   大小: {size_mb:.2f} MB")
        
        return output_path
    
    except Exception as e:
        print(f"❌ 備份失敗: {e}")
        return None


def full_backup() -> Tuple[Optional[Path], Optional[Path]]:
    """執行完整備份（資料庫 + 檔案）"""
    print("\n" + "=" * 60)
    print("🗄️  執行完整備份")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = BACKUP_DIR / f"full_backup_{timestamp}"
    backup_folder.mkdir(exist_ok=True)
    
    # 備份資料庫
    db_backup = backup_database(backup_folder / f"db_{timestamp}.sql.gz")
    
    # 備份檔案
    files_backup = backup_files(backup_folder / f"files_{timestamp}.tar.gz")
    
    # 建立備份資訊檔案
    info_file = backup_folder / "backup_info.txt"
    info_content = f"""Backup Information
====================
Timestamp: {timestamp}
Date: {datetime.now().isoformat()}
Type: Full Backup

Components:
- Database: {'OK' if db_backup else 'FAILED'}
- Files: {'OK' if files_backup else 'FAILED'}

Paths:
- Database: {db_backup}
- Files: {files_backup}
"""
    info_file.write_text(info_content)
    
    # 建立完整歸檔
    full_archive = BACKUP_DIR / f"full_backup_{timestamp}.tar.gz"
    with tarfile.open(full_archive, "w:gz") as tar:
        tar.add(backup_folder, arcname=backup_folder.name)
    
    # 清理臨時檔案夾
    shutil.rmtree(backup_folder)
    
    size_mb = full_archive.stat().st_size / 1024 / 1024
    print(f"\n✅ 完整備份完成!")
    print(f"   歸檔: {full_archive}")
    print(f"   總大小: {size_mb:.2f} MB")
    
    return full_archive, (db_backup, files_backup)


def restore_database(backup_file: Path) -> bool:
    """從備份還原資料庫"""
    if not backup_file.exists():
        print(f"❌ 備份檔案不存在: {backup_file}")
        return False
    
    print(f"🔄 還原資料庫...")
    print(f"   來源: {backup_file}")
    
    confirm = input("⚠️  這將覆蓋現有資料庫! 確認繼續? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return False
    
    try:
        # 解壓縮
        sql_file = Path(str(backup_file).replace('.gz', ''))
        if backup_file.suffix == '.gz':
            import gzip
            with gzip.open(backup_file, 'rb') as f_in:
                with open(sql_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        
            # 執行還原
            # 從 DB_CONFIG 讀取 root 密碼
            root_password = DB_CONFIG.get("root_password", "")
            cmd = [
                "docker", "exec", "-i", CONTAINER_DB,
                "mysql", "-u", "root", f"-p{root_password}",
                "wordpress_db"
            ]
        
        with open(sql_file, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        
        # 清理臨時檔案
        if sql_file != backup_file and sql_file.exists():
            sql_file.unlink()
        
        print(f"✅ 資料庫還原完成")
        return True
    
    except Exception as e:
        print(f"❌ 還原失敗: {e}")
        return False


def restore_files(backup_file: Path) -> bool:
    """從備份還原檔案"""
    if not backup_file.exists():
        print(f"❌ 備份檔案不存在: {backup_file}")
        return False
    
    print(f"🔄 還原檔案...")
    print(f"   來源: {backup_file}")
    
    confirm = input("⚠️  這將覆蓋現有 WordPress 檔案! 確認繼續? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return False
    
    try:
        # 備份當前檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = BACKUP_DIR / f"pre_restore_backup_{timestamp}.tar.gz"
        with tarfile.open(current_backup, "w:gz") as tar:
            tar.add(WP_DATA_DIR, arcname="wp_data_backup")
        print(f"   當前檔案已備份到: {current_backup}")
        
        # 清空當前目錄
        shutil.rmtree(WP_DATA_DIR)
        WP_DATA_DIR.mkdir()
        
        # 解壓備份
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(PROJECT_DIR)
        
        print(f"✅ 檔案還原完成")
        return True
    
    except Exception as e:
        print(f"❌ 還原失敗: {e}")
        return False


def list_backups() -> List[Dict[str, Any]]:
    """列出所有備份"""
    print("📋 備份列資料表...")
    
    backups = []
    for file in BACKUP_DIR.iterdir():
        if file.is_file() and ('backup' in file.name or 'backup' in file.suffix):
            stat = file.stat()
            backups.append({
                'name': file.name,
                'path': file,
                'size': stat.st_size / 1024 / 1024,  # MB
                'created': datetime.fromtimestamp(stat.st_mtime),
                'type': 'database' if 'db_' in file.name else ('files' if 'files_' in file.name else 'full')
            })
    
    # 按時間排序
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    return backups


def show_backups():
    """顯示備份列資料表"""
    backups = list_backups()
    
    print("\n" + "=" * 60)
    print(f"💾 備份列資料表 (共 {len(backups)} 個)")
    print("=" * 60)
    
    if not backups:
        print("  沒有找到備份檔案")
        return
    
    for i, backup in enumerate(backups, 1):
        type_icon = "🗄️" if backup['type'] == 'database' else ("📁" if backup['type'] == 'files' else "📦")
        print(f"\n{type_icon} {i}. {backup['name']}")
        print(f"   類型: {backup['type']}")
        print(f"   大小: {backup['size']:.2f} MB")
        print(f"   建立: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")


def cleanup_old_backups(keep_days: int = 30) -> int:
    """清理舊備份"""
    print(f"🧹 清理 {keep_days} 天前的備份...")
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    deleted_count = 0
    
    for file in BACKUP_DIR.iterdir():
        if file.is_file() and 'backup' in file.name:
            file_date = datetime.fromtimestamp(file.stat().st_mtime)
            if file_date < cutoff_date:
                print(f"   刪除: {file.name}")
                file.unlink()
                deleted_count += 1
    
    print(f"✅ 已清理 {deleted_count} 箇舊備份")
    return deleted_count


def get_backup_size() -> Dict[str, float]:
    """取得備份存儲大小統計"""
    total_size = 0
    db_size = 0
    files_size = 0
    full_size = 0
    
    for file in BACKUP_DIR.iterdir():
        if file.is_file():
            size = file.stat().st_size / 1024 / 1024  # MB
            total_size += size
            
            if 'db_' in file.name:
                db_size += size
            elif 'files_' in file.name:
                files_size += size
            elif 'full_' in file.name:
                full_size += size
    
    return {
        'total': total_size,
        'database': db_size,
        'files': files_size,
        'full': full_size
    }


def interactive_restore():
    """交互式還原"""
    backups = list_backups()
    
    if not backups:
        print("沒有可用的備份檔案")
        return
    
    show_backups()
    
    choice = input("\n選擇要還原的備份編號 (或 'cancel' 取消): ").strip()
    
    if choice.lower() == 'cancel':
        print("❌ 操作已取消")
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(backups):
            backup = backups[idx]
            
            print(f"\n選擇的備份: {backup['name']}")
            print(f"類型: {backup['type']}")
            
            if backup['type'] == 'database':
                restore_database(backup['path'])
            elif backup['type'] == 'files':
                restore_files(backup['path'])
            else:
                print("完整備份還原請手動解壓後分別還原資料庫和檔案")
        else:
            print("無效的選擇")
    except ValueError:
        print("請輸入有效的數字")


def schedule_backup(crontab_schedule: str = "0 2 * * *") -> str:
    """設定定時備份 (回傳 cron 設定說明)"""
    script_path = PROJECT_DIR / ".agent" / "skill" / "backup.py"
    
    cron_job = f"{crontab_schedule} cd {PROJECT_DIR} && python3 {script_path} --full >> {PROJECT_DIR}/backups/backup.log 2>&1"
    
    instructions = f"""
定時備份設定說明:
==================

要設定自動備份，請執行以下步驟:

1. 編輯 crontab:
   crontab -e

2. 添加以下行 (每天凌晨 2 點執行):
   {cron_job}

3. 常用定時模式:
   - 每天凌晨 2 點: 0 2 * * *
   - 每小時: 0 * * * *
   - 每週日 3 點: 0 3 * * 0
   - 每月 1 號 4 點: 0 4 1 * *

4. 檢視 cron 日誌:
   tail -f {PROJECT_DIR}/backups/backup.log

當前備份設定:
   備份目錄: {BACKUP_DIR}
   腳本路徑: {script_path}
"""
    
    return instructions


def interactive_cli():
    """交互式 CLI 菜單"""
    while True:
        print("\n" + "=" * 60)
        print("💾 Backup Skill - 備份與還原工具")
        print("=" * 60)
        print("1. 完整備份 (資料庫 + 檔案)")
        print("2. 僅備份資料庫")
        print("3. 僅備份檔案")
        print("4. 檢視備份列資料表")
        print("5. 還原資料庫")
        print("6. 還原檔案")
        print("7. 清理舊備份")
        print("8. 檢視存儲統計")
        print("9. 定時備份設定說明")
        print("0. 結束")
        
        choice = input("\n請選擇操作 [0-9]: ").strip()
        
        if choice == '1':
            full_backup()
            
        elif choice == '2':
            backup_database()
            
        elif choice == '3':
            backup_files()
            
        elif choice == '4':
            show_backups()
            
        elif choice == '5':
            interactive_restore()
            
        elif choice == '6':
            interactive_restore()
            
        elif choice == '7':
            days = input("保留多少天內的備份? (預設 30): ").strip() or "30"
            cleanup_old_backups(int(days))
            
        elif choice == '8':
            stats = get_backup_size()
            print("\n存儲統計:")
            print(f"  資料庫備份: {stats['database']:.2f} MB")
            print(f"  檔案備份: {stats['files']:.2f} MB")
            print(f"  完整備份: {stats['full']:.2f} MB")
            print(f"  總計: {stats['total']:.2f} MB")
            
        elif choice == '9':
            print(schedule_backup())
            
        elif choice == '0':
            print("再見!")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--full':
            full_backup()
        elif sys.argv[1] == '--db':
            backup_database()
        elif sys.argv[1] == '--files':
            backup_files()
        else:
            interactive_cli()
    else:
        interactive_cli()
