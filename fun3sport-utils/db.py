#!/usr/bin/env python3
"""
Database Skill - WordPress MariaDB 資料庫操作工具集
提供完整的資料庫管理、查詢、維護功能
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 從 __init__.py 導入配置
from . import (
    PROJECT_DIR, CONTAINER_DB, CONTAINER_WP, DB_CONFIG,
    BACKUP_DIR, check_sensitive_config
)


def run_mysql_command(sql: str, use_root: bool = False) -> str:
    """在資料庫容器中執行 MySQL 指令"""
    user = "root" if use_root else DB_CONFIG["user"]
    password = DB_CONFIG["root_password"] if use_root else DB_CONFIG["password"]
    
    cmd = [
        "docker", "exec", CONTAINER_DB,
        "mysql", "-u", user, f"-p{password}",
        "-e", sql
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


def run_mysql_interactive():
    """啟動交互式 MySQL 會話"""
    print("🗄️  啟動交互式 MySQL 會話 (使用 wp_user)...")
    print("提示: 輸入 SQL 指令，輸入 'exit' 或 'quit' 結束")
    print("-" * 50)
    
    cmd = [
        "docker", "exec", "-it", CONTAINER_DB,
        "mysql", "-u", DB_CONFIG["user"],
        f"-p{DB_CONFIG['password']}",
        DB_CONFIG["database"]
    ]
    
    subprocess.run(cmd)


def list_tables() -> List[str]:
    """列出資料庫中的所有資料表"""
    print("📋 列出所有資料表格...")
    output = run_mysql_command(f"USE {DB_CONFIG['database']}; SHOW TABLES;")
    
    tables = []
    for line in output.split('\n'):
        line = line.strip()
        if line and not line.startswith('Tables_in') and not line.startswith('+'):
            # 去除資料表格邊框字符
            clean_line = line.strip('| ')
            if clean_line and clean_line not in tables:
                tables.append(clean_line)
    
    return tables


def get_table_structure(table_name: str) -> Dict[str, Any]:
    """取得資料表結構資訊"""
    print(f"🔍 取得資料表 {table_name} 的結構...")
    output = run_mysql_command(f"USE {DB_CONFIG['database']}; DESCRIBE {table_name};")
    
    columns = []
    for line in output.split('\n'):
        line = line.strip()
        if line and not line.startswith('+') and not line.startswith('Field'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3:
                columns.append({
                    'field': parts[0],
                    'type': parts[1],
                    'null': parts[2],
                    'key': parts[3] if len(parts) > 3 else '',
                    'default': parts[4] if len(parts) > 4 else '',
                    'extra': parts[5] if len(parts) > 5 else ''
                })
    
    return {'table': table_name, 'columns': columns}


def get_table_count(table_name: str) -> int:
    """取得資料表的記錄數"""
    output = run_mysql_command(
        f"USE {DB_CONFIG['database']}; SELECT COUNT(*) as count FROM {table_name};"
    )
    
    for line in output.split('\n'):
        line = line.strip()
        if line and line.isdigit():
            return int(line)
    
    return 0


def sample_table_data(table_name: str, limit: int = 5) -> List[Dict]:
    """取得資料表樣本資料"""
    print(f"📊 取得 {table_name} 的 {limit} 條樣本資料...")
    output = run_mysql_command(
        f"USE {DB_CONFIG['database']}; SELECT * FROM {table_name} LIMIT {limit};"
    )
    
    lines = output.strip().split('\n')
    if len(lines) < 3:
        return []
    
    # 解析資料表頭
    headers = [h.strip() for h in lines[1].split('|') if h.strip()]
    
    # 解析資料
    data = []
    for line in lines[3:]:  # 跳過分隔線
        if line.strip() and not line.startswith('+--'):
            values = [v.strip() for v in line.split('|') if v.strip() or v == '']
            if values:
                row = {}
                for i, header in enumerate(headers):
                    row[header] = values[i] if i < len(values) else ''
                data.append(row)
    
    return data


def execute_sql_file(sql_file: Path) -> str:
    """執行 SQL 檔案"""
    if not sql_file.exists():
        return f"Error: File {sql_file} not found"
    
    print(f"📄 執行 SQL 檔案: {sql_file}")
    cmd = [
        "docker", "exec", "-i", CONTAINER_DB,
        "mysql", "-u", "root", f"-p{DB_CONFIG['root_password']}",
        DB_CONFIG["database"]
    ]
    
    try:
        with open(sql_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True, check=True)
        return f"✓ SQL 檔案執行成功\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"✗ 執行失敗: {e.stderr}"


def backup_database(backup_dir: Optional[Path] = None) -> Path:
    """備份資料庫"""
    if backup_dir is None:
        backup_dir = PROJECT_DIR / "backups"
    
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"wordpress_db_backup_{timestamp}.sql"
    
    print(f"💾 備份資料庫到: {backup_file}")
    
    cmd = [
        "docker", "exec", CONTAINER_DB,
        "mysqldump", "-u", "root", f"-p{DB_CONFIG['root_password']}",
        "--databases", DB_CONFIG["database"],
        "--single-transaction",
        "--routines",
        "--triggers"
    ]
    
    try:
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        print(f"✓ 備份完成: {backup_file}")
        print(f"  檔案大小: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"✗ 備份失敗: {e}")
        return None


def restore_database(backup_file: Path) -> bool:
    """從備份檔案還原資料庫"""
    if not backup_file.exists():
        print(f"✗ 備份檔案不存在: {backup_file}")
        return False
    
    print(f"🔄 從 {backup_file} 還原資料庫...")
    print("⚠️  這將覆蓋現有資料庫！")
    
    result = input("確認還原? (yes/no): ")
    if result.lower() != 'yes':
        print("❌ 操作已取消")
        return False
    
    return execute_sql_file(backup_file) is not None


def get_wp_options(option_names: List[str] = None) -> Dict[str, str]:
    """取得 WordPress 選項"""
    if option_names is None:
        option_names = ['siteurl', 'home', 'blogname', 'blogdescription', 'admin_email']
    
    placeholders = ','.join([f"'{n}'" for n in option_names])
    output = run_mysql_command(
        f"USE {DB_CONFIG['database']}; SELECT option_name, option_value FROM wp_options WHERE option_name IN ({placeholders});"
    )
    
    options = {}
    for line in output.split('\n'):
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) == 2 and not parts[0].startswith('+-') and parts[0] != 'option_name':
            options[parts[0]] = parts[1]
    
    return options


def update_wp_option(option_name: str, option_value: str) -> bool:
    """更新 WordPress 選項"""
    output = run_mysql_command(
        f"USE {DB_CONFIG['database']}; UPDATE wp_options SET option_value = '{option_value}' WHERE option_name = '{option_name}';"
    )
    print(f"✓ 更新 {option_name} = {option_value}")
    return 'error' not in output.lower()


def get_db_stats() -> Dict[str, Any]:
    """取得資料庫統計資訊"""
    print("📈 取得資料庫統計...")
    
    # 資料庫大小
    size_output = run_mysql_command(
        f"USE {DB_CONFIG['database']}; SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)' FROM information_schema.TABLES WHERE table_schema = '{DB_CONFIG['database']}' ORDER BY (data_length + index_length) DESC;"
    )
    
    # 資料表數量
    tables = list_tables()
    
    stats = {
        'tables_count': len(tables),
        'tables': tables,
        'size_details': size_output
    }
    
    return stats


def check_db_health() -> Dict[str, Any]:
    """檢查資料庫健康狀態"""
    print("🏥 檢查資料庫健康狀態...")
    
    checks = {}
    
    # 檢查連線
    try:
        output = run_mysql_command("SELECT 1;")
        checks['connection'] = '✓' in output or '1' in output
    except Exception:
        checks['connection'] = False
    
    # 檢查資料表狀態
    tables = list_tables()
    checks['tables'] = len(tables) > 0
    
    # 檢查特定關鍵資料表
    critical_tables = ['wp_posts', 'wp_users', 'wp_options']
    checks['critical_tables'] = all(t in tables for t in critical_tables)
    
    return checks


def repair_table(table_name: str) -> bool:
    """修復資料表"""
    print(f"🔧 修復資料表: {table_name}")
    output = run_mysql_command(f"USE {DB_CONFIG['database']}; REPAIR TABLE {table_name};")
    return 'OK' in output


def optimize_table(table_name: str) -> bool:
    """優化資料表"""
    print(f"⚡ 優化資料表: {table_name}")
    output = run_mysql_command(f"USE {DB_CONFIG['database']}; OPTIMIZE TABLE {table_name};")
    return 'OK' in output


def interactive_cli():
    """交互式 CLI 菜單"""
    while True:
        print("\n" + "=" * 60)
        print("🗄️  Database Skill - WordPress MariaDB 管理工具")
        print("=" * 60)
        print("1. 列出所有資料表")
        print("2. 檢視資料表結構")
        print("3. 檢視資料表資料樣本")
        print("4. 執行 SQL 檔案")
        print("5. 備份資料庫")
        print("6. 還原資料庫")
        print("7. 檢視 WordPress 設定")
        print("8. 資料庫健康檢查")
        print("9. 進入交互式 MySQL")
        print("0. 結束")
        
        choice = input("\n請選擇操作 [0-9]: ").strip()
        
        if choice == '1':
            tables = list_tables()
            print(f"\n找到 {len(tables)} 個資料表:")
            for i, t in enumerate(tables, 1):
                count = get_table_count(t)
                print(f"  {i}. {t} ({count} 條記錄)")
                
        elif choice == '2':
            table = input("請輸入資料表名: ").strip()
            if table:
                structure = get_table_structure(table)
                print(f"\n資料表: {structure['table']}")
                print("-" * 60)
                for col in structure['columns']:
                    print(f"  {col['field']}: {col['type']} {col['null']}")
                    
        elif choice == '3':
            table = input("請輸入資料表名: ").strip()
            limit = input("顯示條數 (預設 5): ").strip() or "5"
            if table:
                data = sample_table_data(table, int(limit))
                print(f"\n{table} 資料樣本:")
                for i, row in enumerate(data, 1):
                    print(f"\n  [{i}]")
                    for k, v in row.items():
                        print(f"    {k}: {v}")
                        
        elif choice == '4':
            file_path = input("請輸入 SQL 檔案路徑: ").strip()
            if file_path:
                result = execute_sql_file(Path(file_path))
                print(result)
                
        elif choice == '5':
            backup_database()
            
        elif choice == '6':
            file_path = input("請輸入備份檔案路徑: ").strip()
            if file_path:
                restore_database(Path(file_path))
                
        elif choice == '7':
            options = get_wp_options()
            print("\nWordPress 設定:")
            for k, v in options.items():
                print(f"  {k}: {v}")
                
        elif choice == '8':
            health = check_db_health()
            print("\n資料庫健康檢查:")
            for k, v in health.items():
                status = "✓" if v else "✗"
                print(f"  {k}: {status}")
                
        elif choice == '9':
            run_mysql_interactive()
            
        elif choice == '0':
            print("再見!")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    interactive_cli()
