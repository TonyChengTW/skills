#!/usr/bin/env python3
"""
Health Check Skill - 系統健康檢查工具集
提供全面的系統健康檢查、診斷和報告功能
"""

import subprocess
import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# 從 __init__.py 導入配置
from . import (
    PROJECT_DIR, CONTAINER_WP, CONTAINER_DB, WP_CONFIG, DB_CONFIG,
    check_sensitive_config
)

WP_URL = WP_CONFIG["url"]


def run_command(cmd: List[str]) -> tuple:
    """執行 shell 指令"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def check_docker_daemon() -> Tuple[bool, str]:
    """檢查 Docker 守護進程"""
    _, _, code = run_command(["docker", "version"])
    if code == 0:
        return True, "Docker 守護進程執行正常"
    else:
        return False, "Docker 守護進程未執行或無法訪問"


def check_container_status(container_name: str) -> Tuple[bool, str]:
    """檢查容器狀態"""
    stdout, _, code = run_command(
        ["docker", "inspect", "--format", "{{.State.Status}}", container_name]
    )
    
    if code != 0:
        return False, f"容器 {container_name} 不存在"
    
    status = stdout.strip()
    if status == "running":
        return True, f"容器 {container_name} 執行中"
    else:
        return False, f"容器 {container_name} 狀態: {status}"


def check_container_health(container_name: str) -> Tuple[bool, str]:
    """檢查容器健康狀態"""
    stdout, _, code = run_command(
        ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name]
    )
    
    if code != 0:
        return True, f"容器 {container_name} 無健康檢查設定"
    
    health = stdout.strip()
    if health == "healthy" or health == "":
        return True, f"容器 {container_name} 健康"
    else:
        return False, f"容器 {container_name} 健康狀態: {health}"


def check_wp_container() -> Tuple[bool, str]:
    """檢查 WordPress 容器"""
    return check_container_status(CONTAINER_WP)


def check_db_container() -> Tuple[bool, str]:
    """檢查資料庫容器"""
    return check_container_status(CONTAINER_DB)


def check_wordpress_response() -> Tuple[bool, str]:
    """檢查 WordPress 網站響應"""
    try:
        import urllib.request
        import ssl
        
        # 忽略 SSL 驗證（如果使用 HTTPS）
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            WP_URL,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            status = response.getcode()
            if status == 200:
                return True, f"WordPress 響應正常 (HTTP {status})"
            else:
                return False, f"WordPress 響應異常 (HTTP {status})"
    except Exception as e:
        return False, f"WordPress 無法訪問: {str(e)}"


def check_database_connection() -> Tuple[bool, str]:
    """檢查資料庫連線"""
    # 從 DB_CONFIG 讀取密碼
    db_password = DB_CONFIG.get("password", "")
    cmd = [
        "docker", "exec", CONTAINER_DB,
        "mysql", "-u", "wp_user", f"-p{db_password}",
        "-e", "SELECT 1;"
    ]
    
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        return True, "資料庫連線正常"
    else:
        return False, f"資料庫連線失敗: {stderr}"


def check_disk_space() -> Tuple[bool, str]:
    """檢查磁碟空間"""
    stdout, _, code = run_command(["df", "-h", str(PROJECT_DIR)])
    
    if code != 0:
        return False, "無法取得磁碟空間資訊"
    
    # 解析磁碟使用率
    lines = stdout.strip().split('\n')
    if len(lines) >= 2:
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                usage_str = parts[4].replace('%', '')
                try:
                    usage = int(usage_str)
                    if usage > 90:
                        return False, f"磁碟使用率過高: {usage}%"
                    elif usage > 80:
                        return True, f"磁碟使用率警告: {usage}%"
                    else:
                        return True, f"磁碟空間正常: {usage}%"
                except ValueError:
                    continue
    
    return True, "磁碟空間檢查完成"


def check_memory() -> Tuple[bool, str]:
    """檢查內存使用"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        
        mem_total = 0
        mem_available = 0
        
        for line in lines:
            if 'MemTotal' in line:
                mem_total = int(line.split()[1]) / 1024 / 1024  # GB
            elif 'MemAvailable' in line:
                mem_available = int(line.split()[1]) / 1024 / 1024  # GB
        
        if mem_total > 0:
            usage_percent = (1 - mem_available / mem_total) * 100
            if usage_percent > 95:
                return False, f"內存使用率過高: {usage_percent:.1f}%"
            elif usage_percent > 85:
                return True, f"內存使用率警告: {usage_percent:.1f}%"
            else:
                return True, f"內存使用正常: {usage_percent:.1f}%"
        
        return True, "內存檢查完成"
    
    except Exception as e:
        return False, f"無法檢查內存: {str(e)}"


def check_network() -> Tuple[bool, str]:
    """檢查網路連線"""
    try:
        # 嘗試解析 localhost
        socket.gethostbyname('localhost')
        return True, "網路連線正常"
    except Exception as e:
        return False, f"網路檢查失敗: {str(e)}"


def check_wordpress_files() -> Tuple[bool, str]:
    """檢查 WordPress 檔案完整性"""
    wp_config = PROJECT_DIR / "wp_data" / "wp-config.php"
    
    if not wp_config.exists():
        return False, "wp-config.php 不存在"
    
    # 檢查關鍵目錄
    required_dirs = [
        PROJECT_DIR / "wp_data" / "wp-content",
        PROJECT_DIR / "wp_data" / "wp-admin",
        PROJECT_DIR / "wp_data" / "wp-includes"
    ]
    
    missing = []
    for d in required_dirs:
        if not d.exists():
            missing.append(d.name)
    
    if missing:
        return False, f"缺少目錄: {', '.join(missing)}"
    
    return True, "WordPress 檔案完整"


def check_database_size() -> Tuple[bool, str]:
    """檢查資料庫大小"""
    # 從 DB_CONFIG 讀取 root 密碼
    root_password = DB_CONFIG.get("root_password", "")
    cmd = [
        "docker", "exec", CONTAINER_DB,
        "mysql", "-u", "root", f"-p{root_password}",
        "-e", "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.TABLES WHERE table_schema = 'wordpress_db';"
    ]
    
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        # 解析輸出
        for line in stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('+') and 'Size' not in line:
                try:
                    size_mb = float(line)
                    if size_mb > 1000:
                        return True, f"資料庫大小: {size_mb:.2f} MB (較大)"
                    else:
                        return True, f"資料庫大小: {size_mb:.2f} MB"
                except ValueError:
                    continue
    
    return False, f"無法取得資料庫大小: {stderr}"


def check_wp_config() -> Tuple[bool, str]:
    """檢查 WordPress 設定"""
    wp_config = PROJECT_DIR / "wp_data" / "wp-config.php"
    
    if not wp_config.exists():
        return False, "wp-config.php 不存在"
    
    try:
        content = wp_config.read_text()
        
        # 檢查關鍵設定
        checks = []
        if 'DB_NAME' in content:
            checks.append("DB_NAME")
        if 'DB_USER' in content:
            checks.append("DB_USER")
        if 'DB_PASSWORD' in content:
            checks.append("DB_PASSWORD")
        
        if len(checks) >= 3:
            return True, f"wp-config.php 設定正常 ({', '.join(checks)})"
        else:
            return False, f"wp-config.php 設定不完整"
    
    except Exception as e:
        return False, f"無法讀取 wp-config.php: {str(e)}"


def check_backup_directory() -> Tuple[bool, str]:
    """檢查備份目錄"""
    backup_dir = PROJECT_DIR / "backups"
    
    if not backup_dir.exists():
        backup_dir.mkdir(exist_ok=True)
        return True, "備份目錄已建立"
    
    # 檢查備份檔案數量
    backups = list(backup_dir.glob("*backup*"))
    if len(backups) == 0:
        return True, "備份目錄為空 (建議定期備份)"
    else:
        return True, f"找到 {len(backups)} 個備份檔案"


def check_log_files() -> Tuple[bool, str]:
    """檢查日誌檔案"""
    log_files = []
    
    # 檢查 Docker 日誌
    for container in [CONTAINER_WP, CONTAINER_DB]:
        stdout, _, code = run_command(["docker", "logs", "--tail", "1", container])
        if code == 0:
            log_files.append(f"{container}: OK")
        else:
            log_files.append(f"{container}: Error")
    
    return True, f"日誌檢查: {', '.join(log_files)}"


def get_system_info() -> Dict[str, Any]:
    """取得系統資訊"""
    info = {
        'timestamp': datetime.now().isoformat(),
        'project_dir': str(PROJECT_DIR),
        'wordpress_url': WP_URL,
    }
    
    # Docker 版本
    stdout, _, _ = run_command(["docker", "version", "--format", "{{.Server.Version}}"])
    info['docker_version'] = stdout.strip() or "Unknown"
    
    # 容器資訊
    for container in [CONTAINER_WP, CONTAINER_DB]:
        stdout, _, code = run_command(
            ["docker", "inspect", "--format", "{{.State.Status}}", container]
        )
        info[f'{container}_status'] = stdout.strip() if code == 0 else "not_found"
    
    return info


def run_full_check() -> Dict[str, Tuple[bool, str]]:
    """執行完整健康檢查"""
    print("🏥 執行系統健康檢查...")
    
    checks = {
        'Docker 守護進程': check_docker_daemon,
        'WordPress 容器': check_wp_container,
        '資料庫容器': check_db_container,
        'WordPress 網站': check_wordpress_response,
        '資料庫連線': check_database_connection,
        '磁碟空間': check_disk_space,
        '內存使用': check_memory,
        '網路連線': check_network,
        'WordPress 檔案': check_wordpress_files,
        '資料庫大小': check_database_size,
        'WP 設定': check_wp_config,
        '備份目錄': check_backup_directory,
        '日誌檔案': check_log_files,
    }
    
    results = {}
    for name, check_func in checks.items():
        print(f"  檢查 {name}...")
        try:
            status, message = check_func()
            results[name] = (status, message)
        except Exception as e:
            results[name] = (False, f"檢查失敗: {str(e)}")
    
    return results


def print_health_report(results: Dict[str, Tuple[bool, str]]):
    """列印健康報告"""
    print("\n" + "=" * 60)
    print("📊 系統健康報告")
    print("=" * 60)
    
    passed = sum(1 for status, _ in results.values() if status)
    failed = len(results) - passed
    
    print(f"\n總計: {len(results)} 項檢查")
    print(f"✅ 透過: {passed}")
    print(f"❌ 失敗: {failed}")
    
    print("\n詳細結果:")
    print("-" * 60)
    
    for name, (status, message) in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
        print(f"   {message}")
    
    print("=" * 60)
    
    if failed == 0:
        print("🎉 所有檢查透過！系統健康")
    elif failed <= 2:
        print("⚠️  系統基本健康，有輕微問題")
    else:
        print("🚨 系統存在多個問題，需要關注")


def save_health_report(results: Dict[str, Tuple[bool, str]], output_path: Optional[Path] = None):
    """儲存健康報告"""
    if output_path is None:
        output_path = PROJECT_DIR / "backups" / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        "Fun3sport WordPress Health Report",
        "=" * 60,
        f"Generated: {datetime.now().isoformat()}",
        "",
        "Summary:",
        f"  Total checks: {len(results)}",
        f"  Passed: {sum(1 for status, _ in results.values() if status)}",
        f"  Failed: {sum(1 for status, _ in results.values() if not status)}",
        "",
        "Details:",
        "-" * 60,
    ]
    
    for name, (status, message) in results.items():
        status_str = "PASS" if status else "FAIL"
        lines.append(f"[{status_str}] {name}")
        lines.append(f"    {message}")
        lines.append("")
    
    output_path.write_text('\n'.join(lines))
    print(f"\n💾 健康報告已儲存到: {output_path}")


def interactive_cli():
    """交互式 CLI 菜單"""
    while True:
        print("\n" + "=" * 60)
        print("🏥 Health Check Skill - 系統健康檢查")
        print("=" * 60)
        print("1. 執行完整健康檢查")
        print("2. 檢查 Docker 狀態")
        print("3. 檢查 WordPress 容器")
        print("4. 檢查資料庫連線")
        print("5. 檢查網站可訪問性")
        print("6. 檢視系統資訊")
        print("7. 儲存健康報告")
        print("0. 結束")
        
        choice = input("\n請選擇操作 [0-7]: ").strip()
        
        if choice == '1':
            results = run_full_check()
            print_health_report(results)
            
        elif choice == '2':
            status, msg = check_docker_daemon()
            icon = "✅" if status else "❌"
            print(f"{icon} {msg}")
            
        elif choice == '3':
            status, msg = check_wp_container()
            icon = "✅" if status else "❌"
            print(f"{icon} {msg}")
            if status:
                status2, msg2 = check_container_health(CONTAINER_WP)
                icon2 = "✅" if status2 else "⚠️"
                print(f"{icon2} {msg2}")
                
        elif choice == '4':
            status, msg = check_database_connection()
            icon = "✅" if status else "❌"
            print(f"{icon} {msg}")
            
        elif choice == '5':
            status, msg = check_wordpress_response()
            icon = "✅" if status else "❌"
            print(f"{icon} {msg}")
            
        elif choice == '6':
            info = get_system_info()
            print("\n系統資訊:")
            for key, value in info.items():
                print(f"  {key}: {value}")
                
        elif choice == '7':
            results = run_full_check()
            print_health_report(results)
            save_health_report(results)
            
        elif choice == '0':
            print("再見!")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--full':
            results = run_full_check()
            print_health_report(results)
        elif sys.argv[1] == '--save':
            results = run_full_check()
            print_health_report(results)
            save_health_report(results)
        else:
            interactive_cli()
    else:
        interactive_cli()
