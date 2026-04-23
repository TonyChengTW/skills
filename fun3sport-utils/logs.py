#!/usr/bin/env python3
"""
Logs Skill - 日誌分析與管理工具集
提供 WordPress、Docker、Nginx 等日誌的檢視、搜尋、分析功能
"""

import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter

# 專案設定
PROJECT_DIR = Path("/home/fun3sport")
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
WP_LOG_PATH = PROJECT_DIR / "wp_data" / "wp-content" / "debug.log"


def run_command(cmd: List[str], capture: bool = True) -> tuple:
    """執行 shell 指令"""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout, result.stderr, result.returncode
        else:
            result = subprocess.run(cmd, check=True)
            return "", "", result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def get_docker_logs(container_name: str, lines: int = 100, since: Optional[str] = None) -> str:
    """取得 Docker 容器日誌"""
    cmd = ["docker", "logs", "--tail", str(lines)]
    if since:
        cmd.extend(["--since", since])
    cmd.append(container_name)
    
    stdout, stderr, code = run_command(cmd)
    return stdout if code == 0 else stderr


def analyze_wordpress_logs(lines: int = 100) -> Dict[str, Any]:
    """分析 WordPress 日誌"""
    print("📜 分析 WordPress 日誌...")
    
    logs = get_docker_logs(CONTAINER_WP, lines)
    
    if not logs.strip():
        print("⚠️  沒有 WordPress 容器日誌")
        return {}
    
    # 統計錯誤類型
    error_patterns = {
        'PHP Fatal Error': r'PHP Fatal error',
        'PHP Warning': r'PHP Warning',
        'PHP Notice': r'PHP Notice',
        'PHP Parse Error': r'PHP Parse error',
        'MySQL Error': r'Error \[mysql\]',
        'WordPress Error': r'WordPress database error',
        '404 Errors': r'404',
        '500 Errors': r'500',
    }
    
    stats = {}
    for error_type, pattern in error_patterns.items():
        matches = re.findall(pattern, logs, re.IGNORECASE)
        stats[error_type] = len(matches)
    
    return {
        'total_lines': len(logs.split('\n')),
        'errors': stats,
        'recent_logs': logs.split('\n')[-20:]  # 最後 20 行
    }


def analyze_db_logs(lines: int = 100) -> Dict[str, Any]:
    """分析資料庫日誌"""
    print("📜 分析資料庫日誌...")
    
    logs = get_docker_logs(CONTAINER_DB, lines)
    
    if not logs.strip():
        print("⚠️  沒有資料庫容器日誌")
        return {}
    
    # 統計資料庫相關指標
    patterns = {
        'Slow Queries': r'\d+\s+seconds',
        'Connections': r'\d+\s+connect',
        'Errors': r'ERROR',
        'Warnings': r'WARNING',
    }
    
    stats = {}
    for log_type, pattern in patterns.items():
        matches = re.findall(pattern, logs, re.IGNORECASE)
        stats[log_type] = len(matches)
    
    return {
        'total_lines': len(logs.split('\n')),
        'stats': stats,
        'recent_logs': logs.split('\n')[-20:]
    }


def analyze_docker_logs(container: Optional[str] = None, lines: int = 100) -> Dict[str, Any]:
    """分析 Docker 容器日誌"""
    if container is None:
        # 分析所有容器
        results = {}
        for c in [CONTAINER_WP, CONTAINER_DB]:
            print(f"📜 分析 {c} 日誌...")
            results[c] = get_docker_logs(c, lines)
        return results
    else:
        print(f"📜 分析 {container} 日誌...")
        return {'container': container, 'logs': get_docker_logs(container, lines)}


def search_errors(keyword: Optional[str] = None, case_sensitive: bool = False) -> List[str]:
    """搜尋日誌中的錯誤"""
    print("🔍 搜尋錯誤日誌...")
    
    # 取得兩個容器的日誌
    wp_logs = get_docker_logs(CONTAINER_WP, lines=1000)
    db_logs = get_docker_logs(CONTAINER_DB, lines=1000)
    
    all_logs = wp_logs + "\n" + db_logs
    lines = all_logs.split('\n')
    
    # 錯誤關鍵字
    error_keywords = [
        'error', 'fatal', 'warning', 'exception', 'failed',
        'critical', 'emergency', 'alert', 'parse error'
    ]
    
    if keyword:
        error_keywords.append(keyword)
    
    found_errors = []
    
    for line in lines:
        for kw in error_keywords:
            if case_sensitive:
                if kw in line:
                    found_errors.append(line.strip())
                    break
            else:
                if kw.lower() in line.lower():
                    found_errors.append(line.strip())
                    break
    
    return found_errors


def follow_logs(container: Optional[str] = None):
    """實時跟蹤日誌"""
    if container:
        print(f"📡 正在跟蹤 {container} 日誌 (按 Ctrl+C 停止)...")
        subprocess.run(["docker", "logs", "-f", container])
    else:
        print("📡 正在跟蹤所有容器日誌 (按 Ctrl+C 停止)...")
        subprocess.run(["docker-compose", "-f", str(PROJECT_DIR / "docker-compose.yml"), "logs", "-f"])


def get_error_summary(hours: int = 24) -> Dict[str, Any]:
    """取得錯誤摘要"""
    print(f"📊 分析過去 {hours} 小時的錯誤...")
    
    since = f"{hours}h"
    wp_logs = get_docker_logs(CONTAINER_WP, lines=1000, since=since)
    db_logs = get_docker_logs(CONTAINER_DB, lines=1000, since=since)
    
    # 統計錯誤
    error_types = Counter()
    
    for log in [wp_logs, db_logs]:
        # PHP 錯誤
        php_errors = re.findall(r'PHP\s+(\w+)\s+error', log, re.IGNORECASE)
        error_types.update([f"PHP {e}" for e in php_errors])
        
        # MySQL 錯誤
        mysql_errors = re.findall(r'Error\s+\[mysql\]', log, re.IGNORECASE)
        error_types.update(['MySQL Error'] * len(mysql_errors))
        
        # WordPress 錯誤
        wp_errors = re.findall(r'WordPress\s+database\s+error', log, re.IGNORECASE)
        error_types.update(['WordPress DB Error'] * len(wp_errors))
        
        # 500 錯誤
        errors_500 = re.findall(r'500', log)
        error_types.update(['HTTP 500'] * len(errors_500))
    
    return dict(error_types)


def export_logs(output_path: Path, container: Optional[str] = None, lines: int = 1000) -> bool:
    """導出日誌到檔案"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 導出日誌到: {output_path}")
    
    if container:
        logs = get_docker_logs(container, lines)
    else:
        # 導出所有容器日誌
        wp_logs = get_docker_logs(CONTAINER_WP, lines)
        db_logs = get_docker_logs(CONTAINER_DB, lines)
        logs = f"=== WordPress Container ===\n{wp_logs}\n\n=== Database Container ===\n{db_logs}"
    
    output_path.write_text(logs)
    print(f"✓ 日誌已導出: {output_path}")
    return True


def analyze_log_patterns() -> Dict[str, Any]:
    """分析日誌模式"""
    print("📈 分析日誌模式...")
    
    # 取得最近日誌
    wp_logs = get_docker_logs(CONTAINER_WP, lines=500)
    
    analysis = {
        'request_patterns': {},
        'error_patterns': {},
        'time_distribution': {}
    }
    
    # 分析請求
    requests = re.findall(r'(GET|POST|PUT|DELETE)\s+([^\s]+)', wp_logs)
    if requests:
        analysis['request_patterns'] = Counter([r[0] for r in requests]).most_common(5)
    
    # 分析時間分佈
    times = re.findall(r'\d{2}:\d{2}:\d{2}', wp_logs)
    if times:
        hours = [t.split(':')[0] for t in times]
        analysis['time_distribution'] = Counter(hours).most_common(5)
    
    return analysis


def show_error_summary():
    """顯示錯誤摘要"""
    print("\n" + "=" * 60)
    print("📊 錯誤摘要")
    print("=" * 60)
    
    errors = get_error_summary(hours=24)
    
    if errors:
        print(f"\n過去 24 小時錯誤統計:")
        for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_type}: {count} 次")
    else:
        print("\n✅ 過去 24 小時沒有檢測到錯誤")


def interactive_cli():
    """交互式 CLI 菜單"""
    while True:
        print("\n" + "=" * 60)
        print("📜 Logs Skill - 日誌分析工具")
        print("=" * 60)
        print("1. 分析 WordPress 日誌")
        print("2. 分析資料庫日誌")
        print("3. 分析 Docker 日誌")
        print("4. 搜尋錯誤")
        print("5. 實時跟蹤日誌")
        print("6. 錯誤摘要報告")
        print("7. 導出日誌")
        print("8. 分析日誌模式")
        print("0. 結束")
        
        choice = input("\n請選擇操作 [0-8]: ").strip()
        
        if choice == '1':
            lines = input("檢視行數 (預設 100): ").strip() or "100"
            result = analyze_wordpress_logs(int(lines))
            if result:
                print(f"\n總日誌行數: {result['total_lines']}")
                print("\n錯誤統計:")
                for error, count in result['errors'].items():
                    if count > 0:
                        print(f"  {error}: {count}")
                print("\n最近日誌:")
                for line in result['recent_logs'][-10:]:
                    if line.strip():
                        print(f"  {line}")
                        
        elif choice == '2':
            lines = input("檢視行數 (預設 100): ").strip() or "100"
            result = analyze_db_logs(int(lines))
            if result:
                print(f"\n總日誌行數: {result['total_lines']}")
                print("\n統計:")
                for stat, count in result['stats'].items():
                    if count > 0:
                        print(f"  {stat}: {count}")
                        
        elif choice == '3':
            print("選擇容器:")
            print(f"  1. {CONTAINER_WP}")
            print(f"  2. {CONTAINER_DB}")
            print("  3. 全部")
            c = input("選擇: ").strip()
            lines = input("檢視行數 (預設 100): ").strip() or "100"
            
            if c == '1':
                result = analyze_docker_logs(CONTAINER_WP, int(lines))
                print(result.get('logs', ''))
            elif c == '2':
                result = analyze_docker_logs(CONTAINER_DB, int(lines))
                print(result.get('logs', ''))
            else:
                results = analyze_docker_logs(lines=int(lines))
                for container, logs in results.items():
                    print(f"\n=== {container} ===")
                    print(logs[:2000])  # 限制輸出
                    
        elif choice == '4':
            keyword = input("搜尋關鍵字 (可選): ").strip()
            errors = search_errors(keyword if keyword else None)
            if errors:
                print(f"\n找到 {len(errors)} 條錯誤日誌:")
                for i, error in enumerate(errors[:20], 1):
                    print(f"  {i}. {error[:150]}")
                if len(errors) > 20:
                    print(f"  ... 還有 {len(errors) - 20} 條")
            else:
                print("未找到錯誤日誌")
                
        elif choice == '5':
            print("選擇容器:")
            print(f"  1. {CONTAINER_WP}")
            print(f"  2. {CONTAINER_DB}")
            print("  3. 全部")
            c = input("選擇: ").strip()
            
            if c == '1':
                follow_logs(CONTAINER_WP)
            elif c == '2':
                follow_logs(CONTAINER_DB)
            else:
                follow_logs()
                
        elif choice == '6':
            show_error_summary()
            
        elif choice == '7':
            filename = input("導出檔案名 (預設: logs_export.txt): ").strip() or "logs_export.txt"
            output_path = PROJECT_DIR / "backups" / filename
            export_logs(output_path)
            
        elif choice == '8':
            analysis = analyze_log_patterns()
            print("\n日誌模式分析:")
            print(f"\n請求模式: {analysis['request_patterns']}")
            print(f"\n時間分佈: {analysis['time_distribution']}")
            
        elif choice == '0':
            print("再見!")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    interactive_cli()
