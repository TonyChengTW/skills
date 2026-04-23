#!/usr/bin/env python3
"""
Docker Skill - Docker 容器與網路管理工具集
提供完整的容器生命週期管理、日誌檢視、網路管理等功能
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 專案設定
PROJECT_DIR = Path("/home/fun3sport")
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
NETWORK_NAME = "fun3sport_net"
COMPOSE_FILE = PROJECT_DIR / "docker-compose.yml"


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


def container_exists(container_name: str) -> bool:
    """檢查容器是否存在"""
    stdout, _, _ = run_command(
        ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"]
    )
    return container_name in stdout


def container_running(container_name: str) -> bool:
    """檢查容器是否執行中"""
    stdout, _, _ = run_command(
        ["docker", "ps", "--filter", f"name={container_name}", "--filter", "status=running", "--format", "{{.Names}}"]
    )
    return container_name in stdout


def get_container_info(container_name: str) -> Dict[str, Any]:
    """取得容器詳細資訊"""
    stdout, _, code = run_command(
        ["docker", "inspect", "--format", "{{json .}}", container_name]
    )
    
    if code != 0:
        return {}
    
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {}


def list_containers(all_containers: bool = True) -> List[Dict[str, Any]]:
    """列出所有容器"""
    print("📦 列出容器...")
    
    cmd = ["docker", "ps", "--format", "json"]
    if all_containers:
        cmd.insert(2, "-a")
    
    stdout, _, _ = run_command(cmd)
    
    containers = []
    for line in stdout.strip().split('\n'):
        if line:
            try:
                container = json.loads(line)
                containers.append(container)
            except json.JSONDecodeError:
                continue
    
    return containers


def show_containers():
    """顯示容器狀態"""
    print("\n" + "=" * 80)
    print("📦 Docker 容器狀態")
    print("=" * 80)
    
    containers = list_containers(all_containers=True)
    
    # 篩選專案相關容器
    project_containers = [
        c for c in containers 
        if CONTAINER_WP in c.get('Names', []) or CONTAINER_DB in c.get('Names', [])
    ]
    
    if not project_containers:
        print("❌ 未找到專案容器")
        return
    
    for c in project_containers:
        names = c.get('Names', [])
        status = c.get('State', 'unknown')
        ports = c.get('Ports', [])
        
        status_icon = "🟢" if status == 'running' else "🔴"
        print(f"\n{status_icon} {names}")
        print(f"   狀態: {status}")
        print(f"   鏡像: {c.get('Image', 'N/A')}")
        print(f"   建立: {c.get('CreatedAt', 'N/A')}")
        print(f"   端口: {', '.join([str(p) for p in ports]) if ports else '無'}")


def start_container(container_name: str) -> bool:
    """啟動容器"""
    print(f"🚀 啟動容器: {container_name}")
    stdout, stderr, code = run_command(["docker", "start", container_name])
    
    if code == 0:
        print(f"✓ 容器 {container_name} 已啟動")
        return True
    else:
        print(f"✗ 啟動失敗: {stderr}")
        return False


def stop_container(container_name: str, timeout: int = 30) -> bool:
    """停止容器"""
    print(f"🛑 停止容器: {container_name}")
    stdout, stderr, code = run_command(
        ["docker", "stop", "-t", str(timeout), container_name]
    )
    
    if code == 0:
        print(f"✓ 容器 {container_name} 已停止")
        return True
    else:
        print(f"✗ 停止失敗: {stderr}")
        return False


def restart_container(container_name: str) -> bool:
    """重啟容器"""
    print(f"🔄 重啟容器: {container_name}")
    stdout, stderr, code = run_command(["docker", "restart", container_name])
    
    if code == 0:
        print(f"✓ 容器 {container_name} 已重啟")
        return True
    else:
        print(f"✗ 重啟失敗: {stderr}")
        return False


def remove_container(container_name: str, force: bool = False) -> bool:
    """刪除容器"""
    print(f"🗑️  刪除容器: {container_name}")
    
    cmd = ["docker", "rm"]
    if force:
        cmd.append("-f")
    cmd.append(container_name)
    
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        print(f"✓ 容器 {container_name} 已刪除")
        return True
    else:
        print(f"✗ 刪除失敗: {stderr}")
        return False


def view_logs(container_name: str, follow: bool = False, lines: int = 100) -> str:
    """檢視容器日誌"""
    print(f"📜 檢視 {container_name} 日誌...")
    
    cmd = ["docker", "logs", "--tail", str(lines)]
    if follow:
        cmd.append("-f")
    cmd.append(container_name)
    
    if follow:
        # 交互式檢視日誌
        print(f"正在跟蹤 {container_name} 日誌 (按 Ctrl+C 結束)...")
        subprocess.run(cmd)
        return ""
    else:
        stdout, stderr, code = run_command(cmd)
        return stdout if code == 0 else stderr


def exec_command(container_name: str, command: List[str]) -> str:
    """在容器中執行指令"""
    cmd = ["docker", "exec", container_name] + command
    stdout, stderr, code = run_command(cmd)
    return stdout if code == 0 else stderr


def exec_interactive(container_name: str, shell: str = "bash"):
    """進入容器交互式 shell"""
    print(f"💻 進入 {container_name} ({shell})...")
    print("提示: 輸入 'exit' 結束")
    subprocess.run(["docker", "exec", "-it", container_name, shell])


def compose_up(build: bool = False) -> bool:
    """啟動所有服務"""
    print("🚀 啟動 Docker Compose 服務...")
    
    cmd = ["docker-compose", "up", "-d"]
    if build:
        cmd.append("--build")
    
    # 切換到專案目錄
    import os
    original_dir = os.getcwd()
    os.chdir(PROJECT_DIR)
    
    try:
        stdout, stderr, code = run_command(cmd)
        if code == 0:
            print("✓ 服務已啟動")
            show_containers()
            return True
        else:
            print(f"✗ 啟動失敗: {stderr}")
            return False
    finally:
        os.chdir(original_dir)


def compose_down(volumes: bool = False) -> bool:
    """停止並移除所有服務"""
    print("🛑 停止 Docker Compose 服務...")
    
    cmd = ["docker-compose", "down"]
    if volumes:
        cmd.append("-v")
    
    import os
    original_dir = os.getcwd()
    os.chdir(PROJECT_DIR)
    
    try:
        stdout, stderr, code = run_command(cmd)
        if code == 0:
            print("✓ 服務已停止")
            if volumes:
                print("✓ 卷已刪除")
            return True
        else:
            print(f"✗ 停止失敗: {stderr}")
            return False
    finally:
        os.chdir(original_dir)


def compose_restart(service: Optional[str] = None) -> bool:
    """重啟服務"""
    print("🔄 重啟服務...")
    
    cmd = ["docker-compose", "restart"]
    if service:
        cmd.append(service)
    
    import os
    original_dir = os.getcwd()
    os.chdir(PROJECT_DIR)
    
    try:
        stdout, stderr, code = run_command(cmd)
        if code == 0:
            print("✓ 服務已重啟")
            return True
        else:
            print(f"✗ 重啟失敗: {stderr}")
            return False
    finally:
        os.chdir(original_dir)


def compose_logs(service: Optional[str] = None, follow: bool = False) -> str:
    """檢視 Compose 日誌"""
    cmd = ["docker-compose", "logs"]
    if follow:
        cmd.append("-f")
    if service:
        cmd.append(service)
    
    import os
    original_dir = os.getcwd()
    os.chdir(PROJECT_DIR)
    
    try:
        if follow:
            print("正在跟蹤日誌 (按 Ctrl+C 結束)...")
            subprocess.run(cmd)
            return ""
        else:
            stdout, stderr, code = run_command(cmd)
            return stdout if code == 0 else stderr
    finally:
        os.chdir(original_dir)


def get_network_info() -> Dict[str, Any]:
    """取得網路資訊"""
    print("🌐 取得網路資訊...")
    
    stdout, _, code = run_command(
        ["docker", "network", "inspect", "--format", "json", NETWORK_NAME]
    )
    
    if code != 0:
        return {}
    
    try:
        networks = json.loads(stdout)
        return networks[0] if networks else {}
    except (json.JSONDecodeError, IndexError):
        return {}


def show_networks():
    """顯示網路資訊"""
    print("\n" + "=" * 80)
    print("🌐 Docker 網路")
    print("=" * 80)
    
    stdout, _, _ = run_command(["docker", "network", "ls"])
    print(stdout)
    
    print(f"\n專案網路詳情 ({NETWORK_NAME}):")
    network_info = get_network_info()
    if network_info:
        print(f"  驅動: {network_info.get('Driver', 'N/A')}")
        print(f"  範圍: {network_info.get('Scope', 'N/A')}")
        containers = network_info.get('Containers', {})
        if containers:
            print(f"  連線容器:")
            for cid, cinfo in containers.items():
                print(f"    - {cinfo.get('Name', 'Unknown')} ({cinfo.get('IPv4Address', 'N/A')})")
    else:
        print("  未找到網路資訊")


def get_resource_usage(container_name: str) -> Dict[str, Any]:
    """取得容器資源使用情況"""
    stdout, _, code = run_command(
        ["docker", "stats", "--no-stream", "--format", "json", container_name]
    )
    
    if code != 0:
        return {}
    
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {}


def show_stats():
    """顯示資源統計"""
    print("\n" + "=" * 80)
    print("📊 容器資源使用")
    print("=" * 80)
    
    for container in [CONTAINER_WP, CONTAINER_DB]:
        if container_running(container):
            stats = get_resource_usage(container)
            if stats:
                print(f"\n🔵 {container}:")
                print(f"   CPU: {stats.get('CPUPerc', 'N/A')}")
                print(f"   內存: {stats.get('MemUsage', 'N/A')} ({stats.get('MemPerc', 'N/A')})")
                print(f"   網路 I/O: {stats.get('NetIO', 'N/A')}")
                print(f"   磁碟 I/O: {stats.get('BlockIO', 'N/A')}")
            else:
                print(f"\n🔴 {container}: 無法取得統計資訊")
        else:
            print(f"\n⚪ {container}: 未執行")


def cleanup_system(prune_all: bool = False):
    """清理 Docker 系統"""
    print("🧹 清理 Docker 系統...")
    
    if prune_all:
        print("⚠️  這將刪除所有未使用的容器、網路、鏡像和卷！")
        confirm = input("確認執行? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
        
        stdout, stderr, code = run_command(["docker", "system", "prune", "-a", "-f"])
    else:
        stdout, stderr, code = run_command(["docker", "system", "prune", "-f"])
    
    if code == 0:
        print("✓ 清理完成")
        print(stdout)
    else:
        print(f"✗ 清理失敗: {stderr}")


def health_check() -> Dict[str, Any]:
    """Docker 健康檢查"""
    print("🏥 Docker 健康檢查...")
    
    health = {
        'docker_daemon': False,
        'wordpress_container': False,
        'db_container': False,
        'network': False,
        'volumes': False
    }
    
    # 檢查 Docker 守護進程
    _, _, code = run_command(["docker", "version"])
    health['docker_daemon'] = code == 0
    
    # 檢查容器
    health['wordpress_container'] = container_running(CONTAINER_WP)
    health['db_container'] = container_running(CONTAINER_DB)
    
    # 檢查網路
    network_info = get_network_info()
    health['network'] = bool(network_info)
    
    # 檢查卷
    wp_data = PROJECT_DIR / "wp_data"
    db_data = PROJECT_DIR / "db_data"
    health['volumes'] = wp_data.exists() and db_data.exists()
    
    return health


def interactive_cli():
    """交互式 CLI 菜單"""
    while True:
        print("\n" + "=" * 60)
        print("🐳 Docker Skill - 容器與編排管理工具")
        print("=" * 60)
        print("1. 檢視容器狀態")
        print("2. 啟動所有服務 (compose up)")
        print("3. 停止所有服務 (compose down)")
        print("4. 重啟服務")
        print("5. 檢視容器日誌")
        print("6. 進入容器 Shell")
        print("7. 檢視網路資訊")
        print("8. 檢視資源使用")
        print("9. 健康檢查")
        print("10. 清理系統")
        print("11. 啟動單個容器")
        print("12. 停止單個容器")
        print("0. 結束")
        
        choice = input("\n請選擇操作 [0-12]: ").strip()
        
        if choice == '1':
            show_containers()
            
        elif choice == '2':
            compose_up()
            
        elif choice == '3':
            vol = input("同時刪除卷? (y/n): ").strip().lower() == 'y'
            compose_down(volumes=vol)
            
        elif choice == '4':
            service = input("服務名 (留空重啟全部): ").strip()
            compose_restart(service if service else None)
            
        elif choice == '5':
            print("選擇容器:")
            print(f"  1. {CONTAINER_WP}")
            print(f"  2. {CONTAINER_DB}")
            c = input("選擇: ").strip()
            container = CONTAINER_WP if c == '1' else CONTAINER_DB
            follow = input("實時跟蹤? (y/n): ").strip().lower() == 'y'
            view_logs(container, follow=follow)
            
        elif choice == '6':
            print("選擇容器:")
            print(f"  1. {CONTAINER_WP}")
            print(f"  2. {CONTAINER_DB}")
            c = input("選擇: ").strip()
            container = CONTAINER_WP if c == '1' else CONTAINER_DB
            shell = input("Shell 類型 (bash/sh): ").strip() or "bash"
            exec_interactive(container, shell)
            
        elif choice == '7':
            show_networks()
            
        elif choice == '8':
            show_stats()
            
        elif choice == '9':
            health = health_check()
            print("\n健康檢查結果:")
            for k, v in health.items():
                status = "✓" if v else "✗"
                print(f"  {k}: {status}")
                
        elif choice == '10':
            prune = input("深度清理 (刪除所有未使用資源)? (y/n): ").strip().lower() == 'y'
            cleanup_system(prune_all=prune)
            
        elif choice == '11':
            print("選擇容器:")
            print(f"  1. {CONTAINER_WP}")
            print(f"  2. {CONTAINER_DB}")
            c = input("選擇: ").strip()
            container = CONTAINER_WP if c == '1' else CONTAINER_DB
            start_container(container)
            
        elif choice == '12':
            print("選擇容器:")
            print(f"  1. {CONTAINER_WP}")
            print(f"  2. {CONTAINER_DB}")
            c = input("選擇: ").strip()
            container = CONTAINER_WP if c == '1' else CONTAINER_DB
            stop_container(container)
            
        elif choice == '0':
            print("再見!")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    interactive_cli()
