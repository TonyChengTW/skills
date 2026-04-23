#!/usr/bin/env python3
"""
Fun3sport Skill - WordPress Docker 維運管理主入口
整合所有技能模組，提供統一的命令行介面

使用方法:
python3 /home/fun3sport/.agent/skill/main.py [command] [options]

Commands:
cli - 啟動交互式選單
db - 資料庫操作子指令
docker - Docker 容器管理子指令
wp - WordPress 管理子指令
logs - 日誌分析子指令
backup - 備份管理子指令
health - 健康檢查

Examples:
python3 /home/fun3sport/.agent/skill/main.py cli
python3 /home/fun3sport/.agent/skill/main.py db --list-tables
python3 /home/fun3sport/.agent/skill/main.py docker --status
python3 /home/fun3sport/.agent/skill/main.py wp --site-info
python3 /home/fun3sport/.agent/skill/main.py health
"""

import sys
import argparse
from pathlib import Path

# 確保可以導入技能模組
sys.path.insert(0, str(Path(__file__).parent))

import db
import docker as docker_skill
import wordpress
import logs
import backup
import healthcheck


def print_banner():
    """列印歡迎橫幅"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║ 🏃 Fun3sport WordPress Docker 維運管理工具 🏃                 ║
║                                                               ║
║ 版本：1.0.0 | 專案：/home/fun3sport                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")


def main_cli():
    """主交互式選單"""
    print_banner()

    while True:
        print("\n" + "=" * 60)
        print("📋 主選單")
        print("=" * 60)
        print("1. 🗄️ 資料庫管理 (Database Skill)")
        print("2. 🐳 Docker 容器管理 (Docker Skill)")
        print("3. 🌐 WordPress 管理 (WordPress Skill)")
        print("4. 📜 日誌分析 (Logs Skill)")
        print("5. 💾 備份管理 (Backup Skill)")
        print("6. 🏥 健康檢查 (Health Check)")
        print("0. 結束")

        choice = input("\n請選擇操作 [0-6]: ").strip()

        if choice == '1':
            db.interactive_cli()
        elif choice == '2':
            docker_skill.interactive_cli()
        elif choice == '3':
            wordpress.interactive_cli()
        elif choice == '4':
            logs.interactive_cli()
        elif choice == '5':
            backup.interactive_cli()
        elif choice == '6':
            run_health_check()
        elif choice == '0':
            print("\n感謝使用 Fun3sport Skill!")
            break
        else:
            print("無效選擇，請重試")


def run_health_check():
    """執行健康檢查"""
    print_banner()
    print("\n🔍 執行系統健康檢查...\n")

    results = healthcheck.run_full_check()

    print("\n" + "=" * 60)
    print("📊 健康檢查摘要")
    print("=" * 60)

    all_passed = True
    for check_name, (status, message) in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}: {message}")
        if not status:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 所有檢查通過！系統健康")
    else:
        print("⚠️ 發現一些問題，請檢視上述報告")


def db_command(args):
    """資料庫子指令處理"""
    if args.list_tables:
        tables = db.list_tables()
        print(f"\n找到 {len(tables)} 個資料表:")
        for i, t in enumerate(tables, 1):
            print(f" {i}. {t}")

    elif args.structure:
        info = db.get_table_structure(args.structure)
        print(f"\n資料表：{info['table']}")
        for col in info['columns']:
            print(f" {col['field']}: {col['type']}")

    elif args.backup:
        db.backup_database()

    elif args.interactive:
        db.run_mysql_interactive()

    else:
        db.interactive_cli()


def docker_command(args):
    """Docker 子指令處理"""
    if args.status:
        docker_skill.show_containers()

    elif args.up:
        docker_skill.compose_up()

    elif args.down:
        docker_skill.compose_down(volumes=args.volumes)

    elif args.restart:
        docker_skill.compose_restart()

    elif args.logs:
        if args.follow:
            docker_skill.view_logs(args.service or docker_skill.CONTAINER_WP, follow=True)
        else:
            print(docker_skill.view_logs(args.service or docker_skill.CONTAINER_WP, lines=args.lines))

    elif args.shell:
        docker_skill.exec_interactive(args.service or docker_skill.CONTAINER_WP, args.shell_type)

    elif args.networks:
        docker_skill.show_networks()

    elif args.stats:
        docker_skill.show_stats()

    else:
        docker_skill.interactive_cli()


def wp_command(args):
    """WordPress 子指令處理"""
    if args.site_info:
        wordpress.show_site_info()

    elif args.plugins:
        wordpress.show_plugins()

    elif args.themes:
        wordpress.show_themes()

    elif args.users:
        wordpress.show_users()

    elif args.posts:
        wordpress.show_posts()

    elif args.cache_flush:
        wordpress.flush_cache()
        print("快取已清除")

    elif args.maintenance:
        enable = args.mode == 'on'
        wordpress.run_maintenance_mode(enable)
        print(f"維護模式{'啟用' if enable else '關閉'}")

    else:
        wordpress.interactive_cli()


def logs_command(args):
    """日誌子指令處理"""
    if args.wp:
        logs.analyze_wordpress_logs(lines=args.lines)

    elif args.db:
        logs.analyze_db_logs(lines=args.lines)

    elif args.docker:
        logs.analyze_docker_logs(container=args.container, lines=args.lines)

    elif args.errors:
        logs.search_errors()

    elif args.follow:
        logs.follow_logs()

    else:
        logs.interactive_cli()


def backup_command(args):
    """備份子指令處理"""
    if args.full:
        backup.full_backup()

    elif args.db:
        db_file = backup.backup_database()
        if db_file:
            print(f"✓ 資料庫備份完成：{db_file}")

    elif args.files:
        files_archive = backup.backup_files()
        if files_archive:
            print(f"✓ 檔案備份完成：{files_archive}")

    elif args.restore:
        backup.interactive_restore()

    elif args.list:
        backup.list_backups()

    elif args.clean:
        backup.cleanup_old_backups(keep_days=args.keep_days)

    else:
        backup.interactive_cli()


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="Fun3sport WordPress Docker 維運管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
%(prog)s cli              # 啟動交互式選單
%(prog)s db --list-tables # 列出資料庫資料表
%(prog)s docker --status  # 檢視容器狀態
%(prog)s wp --site-info   # 檢視網站資訊
%(prog)s health           # 執行健康檢查
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='可用指令')

    # CLI 指令
    cli_parser = subparsers.add_parser('cli', help='啟動交互式選單')

    # 資料庫指令
    db_parser = subparsers.add_parser('db', help='資料庫管理')
    db_parser.add_argument('--list-tables', action='store_true', help='列出所有資料表')
    db_parser.add_argument('--structure', metavar='TABLE', help='檢視資料表結構')
    db_parser.add_argument('--backup', action='store_true', help='備份資料庫')
    db_parser.add_argument('--interactive', action='store_true', help='進入 MySQL')
    db_parser.set_defaults(func=db_command)

    # Docker 指令
    docker_parser = subparsers.add_parser('docker', help='Docker 管理')
    docker_parser.add_argument('--status', action='store_true', help='檢視容器狀態')
    docker_parser.add_argument('--up', action='store_true', help='啟動服務')
    docker_parser.add_argument('--down', action='store_true', help='停止服務')
    docker_parser.add_argument('--volumes', action='store_true', help='同時刪除卷')
    docker_parser.add_argument('--restart', action='store_true', help='重啟服務')
    docker_parser.add_argument('--logs', action='store_true', help='檢視日誌')
    docker_parser.add_argument('--follow', '-f', action='store_true', help='跟蹤日誌')
    docker_parser.add_argument('--service', '-s', help='指定服務名')
    docker_parser.add_argument('--lines', '-n', type=int, default=100, help='日誌行數')
    docker_parser.add_argument('--shell', action='store_true', help='進入容器 shell')
    docker_parser.add_argument('--shell-type', default='bash', help='Shell 類型')
    docker_parser.add_argument('--networks', action='store_true', help='檢視網路')
    docker_parser.add_argument('--stats', action='store_true', help='檢視資源使用')
    docker_parser.set_defaults(func=docker_command)

    # WordPress 指令
    wp_parser = subparsers.add_parser('wp', help='WordPress 管理')
    wp_parser.add_argument('--site-info', action='store_true', help='檢視網站資訊')
    wp_parser.add_argument('--plugins', action='store_true', help='列出插件')
    wp_parser.add_argument('--themes', action='store_true', help='列出主題')
    wp_parser.add_argument('--users', action='store_true', help='列出使用者')
    wp_parser.add_argument('--posts', action='store_true', help='列出文章')
    wp_parser.add_argument('--cache-flush', action='store_true', help='清除快取')
    wp_parser.add_argument('--maintenance', action='store_true', help='維護模式')
    wp_parser.add_argument('--mode', choices=['on', 'off'], help='維護模式開關')
    wp_parser.set_defaults(func=wp_command)

    # 日誌指令
    logs_parser = subparsers.add_parser('logs', help='日誌分析')
    logs_parser.add_argument('--wp', action='store_true', help='WordPress 日誌')
    logs_parser.add_argument('--db', action='store_true', help='資料庫日誌')
    logs_parser.add_argument('--docker', action='store_true', help='Docker 日誌')
    logs_parser.add_argument('--container', '-c', help='容器名')
    logs_parser.add_argument('--errors', '-e', action='store_true', help='搜尋錯誤')
    logs_parser.add_argument('--follow', '-f', action='store_true', help='跟蹤日誌')
    logs_parser.add_argument('--lines', '-n', type=int, default=50, help='日誌行數')
    logs_parser.set_defaults(func=logs_command)

    # 備份指令
    backup_parser = subparsers.add_parser('backup', help='備份管理')
    backup_parser.add_argument('--full', action='store_true', help='完整備份')
    backup_parser.add_argument('--db', action='store_true', help='僅備份資料庫')
    backup_parser.add_argument('--files', action='store_true', help='僅備份檔案')
    backup_parser.add_argument('--restore', action='store_true', help='還原備份')
    backup_parser.add_argument('--list', action='store_true', help='列出備份')
    backup_parser.add_argument('--clean', action='store_true', help='清理舊備份')
    backup_parser.add_argument('--keep-days', type=int, default=30, help='保留天數')
    backup_parser.set_defaults(func=backup_command)

    # 健康檢查指令
    health_parser = subparsers.add_parser('health', help='健康檢查')

    args = parser.parse_args()

    # 處理指令
    if args.command is None:
        # 沒有子指令，啟動交互式選單
        main_cli()
    elif args.command == 'cli':
        main_cli()
    elif args.command == 'health':
        run_health_check()
    elif hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
