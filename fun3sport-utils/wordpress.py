#!/usr/bin/env python3
"""
WordPress Skill - WordPress 網站運維管理工具集
提供 WP-CLI 操作、網站設定、插件主題管理、性能優化等功能
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 專案設定
PROJECT_DIR = Path("/home/fun3sport")
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
WP_CLI_PATH = "/var/www/html/wp-cli.phar"
WP_CONFIG_PATH = PROJECT_DIR / "wp_data" / "wp-config.php"


def run_wp_cli(command: List[str], json_output: bool = False) -> str:
    """在 WordPress 容器中執行 WP-CLI 指令"""
    cmd = ["docker", "exec", CONTAINER_WP, "php", WP_CLI_PATH, "--allow-root"]
    cmd.extend(command)
    
    if json_output:
        cmd.append("--format=json")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


def get_wp_version() -> str:
    """取得 WordPress 版本"""
    output = run_wp_cli(["core", "version"])
    return output.strip()


def get_site_info() -> Dict[str, str]:
    """取得網站基本資訊"""
    print("ℹ️  取得網站資訊...")
    
    info = {}
    
    # 取得各種資訊
    info['version'] = run_wp_cli(["core", "version"]).strip()
    info['url'] = run_wp_cli(["option", "get", "siteurl"]).strip()
    info['title'] = run_wp_cli(["option", "get", "blogname"]).strip()
    info['description'] = run_wp_cli(["option", "get", "blogdescription"]).strip()
    info['admin_email'] = run_wp_cli(["option", "get", "admin_email"]).strip()
    info['language'] = run_wp_cli(["option", "get", "WPLANG"]).strip() or "en_US"
    info['timezone'] = run_wp_cli(["option", "get", "timezone_string"]).strip() or "UTC"
    
    return info


def show_site_info():
    """顯示網站資訊"""
    info = get_site_info()
    
    print("\n" + "=" * 60)
    print("🌐 WordPress 網站資訊")
    print("=" * 60)
    print(f"  標題: {info['title']}")
    print(f"  URL: {info['url']}")
    print(f"  描述: {info['description']}")
    print(f"  版本: {info['version']}")
    print(f"  語言: {info['language']}")
    print(f"  時區: {info['timezone']}")
    print(f"  管理員郵箱: {info['admin_email']}")


def list_plugins(status: str = "all") -> List[Dict[str, Any]]:
    """列出所有插件"""
    print(f"🔌 列出插件 (狀態: {status})...")
    
    output = run_wp_cli(["plugin", "list", "--format=json"], json_output=True)
    
    try:
        plugins = json.loads(output)
        if status != "all":
            plugins = [p for p in plugins if p.get('status') == status]
        return plugins
    except json.JSONDecodeError:
        return []


def show_plugins():
    """顯示插件列資料表"""
    plugins = list_plugins()
    
    print("\n" + "=" * 60)
    print(f"🔌 插件列資料表 (共 {len(plugins)} 個)")
    print("=" * 60)
    
    active_count = len([p for p in plugins if p.get('status') == 'active'])
    print(f"✅ 已啟用: {active_count} | ⏸️ 未啟用: {len(plugins) - active_count}")
    print("-" * 60)
    
    for i, plugin in enumerate(plugins, 1):
        status_icon = "🟢" if plugin.get('status') == 'active' else "⚪"
        update_icon = "📦" if plugin.get('update') == 'available' else ""
        print(f"{status_icon} {i}. {plugin['name']}")
        print(f"   版本: {plugin.get('version', 'N/A')} {update_icon}")
        print(f"   狀態: {plugin.get('status', 'N/A')}")


def activate_plugin(plugin_name: str) -> bool:
    """啟用插件"""
    print(f"✅ 啟用插件: {plugin_name}")
    output = run_wp_cli(["plugin", "activate", plugin_name])
    return "Success" in output or "已啟用" in output


def deactivate_plugin(plugin_name: str) -> bool:
    """停用插件"""
    print(f"⏸️  停用插件: {plugin_name}")
    output = run_wp_cli(["plugin", "deactivate", plugin_name])
    return "Success" in output or "已停用" in output


def install_plugin(plugin_name: str, activate: bool = True) -> bool:
    """安裝插件"""
    print(f"📥 安裝插件: {plugin_name}")
    cmd = ["plugin", "install", plugin_name]
    if activate:
        cmd.append("--activate")
    output = run_wp_cli(cmd)
    return "Success" in output or "成功" in output


def uninstall_plugin(plugin_name: str) -> bool:
    """卸載插件"""
    print(f"🗑️  卸載插件: {plugin_name}")
    output = run_wp_cli(["plugin", "uninstall", plugin_name, "--deactivate"])
    return "Success" in output or "成功" in output


def update_plugin(plugin_name: Optional[str] = None) -> bool:
    """更新插件"""
    if plugin_name:
        print(f"📦 更新插件: {plugin_name}")
        output = run_wp_cli(["plugin", "update", plugin_name])
    else:
        print("📦 更新所有插件...")
        output = run_wp_cli(["plugin", "update", "--all"])
    return "Success" in output or "成功" in output or "Updated" in output


def list_themes() -> List[Dict[str, Any]]:
    """列出所有主題"""
    print("🎨 列出主題...")
    
    output = run_wp_cli(["theme", "list", "--format=json"], json_output=True)
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def show_themes():
    """顯示主題列資料表"""
    themes = list_themes()
    
    print("\n" + "=" * 60)
    print(f"🎨 主題列資料表 (共 {len(themes)} 個)")
    print("=" * 60)
    
    for i, theme in enumerate(themes, 1):
        status_icon = "🟢" if theme.get('status') == 'active' else "⚪"
        update_icon = "📦" if theme.get('update') == 'available' else ""
        print(f"{status_icon} {i}. {theme['name']}")
        print(f"   版本: {theme.get('version', 'N/A')} {update_icon}")
        print(f"   狀態: {theme.get('status', 'N/A')}")


def activate_theme(theme_name: str) -> bool:
    """啟用主題"""
    print(f"🎨 啟用主題: {theme_name}")
    output = run_wp_cli(["theme", "activate", theme_name])
    return "Success" in output or "成功" in output


def install_theme(theme_name: str, activate: bool = False) -> bool:
    """安裝主題"""
    print(f"📥 安裝主題: {theme_name}")
    cmd = ["theme", "install", theme_name]
    if activate:
        cmd.append("--activate")
    output = run_wp_cli(cmd)
    return "Success" in output or "成功" in output


def delete_theme(theme_name: str) -> bool:
    """刪除主題"""
    print(f"🗑️  刪除主題: {theme_name}")
    output = run_wp_cli(["theme", "delete", theme_name])
    return "Success" in output or "成功" in output


def update_theme(theme_name: Optional[str] = None) -> bool:
    """更新主題"""
    if theme_name:
        print(f"📦 更新主題: {theme_name}")
        output = run_wp_cli(["theme", "update", theme_name])
    else:
        print("📦 更新所有主題...")
        output = run_wp_cli(["theme", "update", "--all"])
    return "Success" in output or "成功" in output or "Updated" in output


def list_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
    """列出使用者"""
    print("👥 列出使用者...")
    
    cmd = ["user", "list", "--format=json"]
    if role:
        cmd.extend(["--role", role])
    
    output = run_wp_cli(cmd, json_output=True)
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def show_users():
    """顯示使用者列資料表"""
    users = list_users()
    
    print("\n" + "=" * 60)
    print(f"👥 使用者列資料表 (共 {len(users)} 人)")
    print("=" * 60)
    
    for i, user in enumerate(users, 1):
        role = user.get('roles', 'N/A')
        role_icon = "👑" if role == 'administrator' else "👤"
        print(f"{role_icon} {i}. {user['display_name']} ({user['user_login']})")
        print(f"   ID: {user['ID']}, 郵箱: {user['user_email']}, 角色: {role}")


def create_user(username: str, email: str, role: str = "subscriber", password: Optional[str] = None) -> bool:
    """建立使用者"""
    print(f"👤 建立使用者: {username}")
    
    cmd = ["user", "create", username, email, f"--role={role}"]
    if password:
        cmd.append(f"--user_pass={password}")
    else:
        cmd.append("--send-email")
    
    output = run_wp_cli(cmd)
    return "Success" in output or "成功" in output or "Created" in output


def delete_user(user_id: int, reassign: Optional[int] = None) -> bool:
    """刪除使用者"""
    print(f"🗑️  刪除使用者 ID: {user_id}")
    
    cmd = ["user", "delete", str(user_id), "--yes"]
    if reassign:
        cmd.append(f"--reassign={reassign}")
    
    output = run_wp_cli(cmd)
    return "Success" in output or "成功" in output or "Deleted" in output


def update_user_password(user_id: int, new_password: str) -> bool:
    """更新使用者密碼"""
    print(f"🔑 更新使用者 ID {user_id} 的密碼")
    output = run_wp_cli(["user", "update", str(user_id), f"--user_pass={new_password}"])
    return "Success" in output or "成功" in output


def update_user_role(user_id: int, role: str) -> bool:
    """更新使用者角色"""
    print(f"👔 更新使用者 ID {user_id} 角色為: {role}")
    output = run_wp_cli(["user", "set-role", str(user_id), role])
    return "Success" in output or "成功" in output


def search_replace(search: str, replace: str, dry_run: bool = True) -> str:
    """搜尋替換資料庫內容"""
    print(f"🔍 搜尋替換: '{search}' → '{replace}'")
    
    if dry_run:
        print("⚠️  當前為預覽模式，不會實際修改資料")
    
    cmd = ["search-replace", search, replace, "--all-tables"]
    if dry_run:
        cmd.append("--dry-run")
    
    output = run_wp_cli(cmd)
    return output


def list_posts(post_type: str = "post", status: str = "any", count: int = 10) -> List[Dict[str, Any]]:
    """列出文章"""
    print(f"📝 列出 {post_type} 類型文章...")
    
    output = run_wp_cli([
        "post", "list",
        f"--post_type={post_type}",
        f"--post_status={status}",
        f"--posts_per_page={count}",
        "--format=json"
    ], json_output=True)
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def show_posts():
    """顯示文章列資料表"""
    posts = list_posts(count=10)
    
    print("\n" + "=" * 60)
    print(f"📝 最近文章 (顯示 {len(posts)} 篇)")
    print("=" * 60)
    
    for i, post in enumerate(posts, 1):
        status_icon = "🟢" if post.get('post_status') == 'publish' else "🟡"
        print(f"{status_icon} {i}. {post.get('post_title', '無標題')}")
        print(f"   ID: {post['ID']}, 類型: {post.get('post_type')}, 狀態: {post.get('post_status')}")
        print(f"   作者: {post.get('post_author')}, 日期: {post.get('post_date')}")


def create_post(title: str, content: str, status: str = "draft") -> bool:
    """建立文章"""
    print(f"📝 建立文章: {title}")
    output = run_wp_cli([
        "post", "create",
        f"--post_title={title}",
        f"--post_content={content}",
        f"--post_status={status}"
    ])
    return "Success" in output or "成功" in output or "Created" in output


def delete_post(post_id: int, force: bool = False) -> bool:
    """刪除文章"""
    print(f"🗑️  刪除文章 ID: {post_id}")
    
    cmd = ["post", "delete", str(post_id)]
    if force:
        cmd.append("--force")
    
    output = run_wp_cli(cmd)
    return "Success" in output or "成功" in output or "Trashed" in output


def update_option(option_name: str, option_value: str) -> bool:
    """更新網站選項"""
    print(f"⚙️  更新選項: {option_name} = {option_value}")
    output = run_wp_cli(["option", "update", option_name, option_value])
    return "Success" in output or "成功" in output or "Updated" in output


def get_option(option_name: str) -> str:
    """取得網站選項"""
    output = run_wp_cli(["option", "get", option_name])
    return output.strip()


def flush_cache() -> bool:
    """清除緩存"""
    print("🧹 清除緩存...")
    output = run_wp_cli(["cache", "flush"])
    return "Success" in output or "成功" in output or "Flushed" in output


def rewrite_flush() -> bool:
    """刷新重寫規則"""
    print("🔄 刷新重寫規則...")
    output = run_wp_cli(["rewrite", "flush"])
    return "Success" in output or "成功" in output


def export_database(export_path: Optional[Path] = None) -> bool:
    """導出資料庫"""
    if export_path is None:
        export_path = PROJECT_DIR / "backups" / f"wp_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    export_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 導出資料庫到: {export_path}")
    output = run_wp_cli(["db", "export", str(export_path)])
    return "Success" in output or "成功" in output or "Exported" in output


def import_database(import_path: Path) -> bool:
    """導入資料庫"""
    if not import_path.exists():
        print(f"✗ 檔案不存在: {import_path}")
        return False
    
    print(f"📥 導入資料庫: {import_path}")
    output = run_wp_cli(["db", "import", str(import_path)])
    return "Success" in output or "成功" in output or "Imported" in output


def check_core() -> str:
    """檢查 WordPress 核心檔案完整性"""
    print("🔍 檢查 WordPress 核心檔案...")
    output = run_wp_cli(["core", "verify-checksums"])
    return output


def update_core(version: Optional[str] = None) -> bool:
    """更新 WordPress 核心"""
    if version:
        print(f"📦 更新 WordPress 到版本 {version}...")
        output = run_wp_cli(["core", "update", f"--version={version}", "--force"])
    else:
        print("📦 更新 WordPress 到最新版本...")
        output = run_wp_cli(["core", "update"])
    
    return "Success" in output or "成功" in output or "Updated" in output


def run_maintenance_mode(enable: bool) -> bool:
    """設定維護模式"""
    if enable:
        print("🔧 啟用維護模式...")
        output = run_wp_cli(["maintenance-mode", "activate"])
    else:
        print("✅ 關閉維護模式...")
        output = run_wp_cli(["maintenance-mode", "deactivate"])
    
    return "Success" in output or "成功" in output


def get_wp_config() -> Dict[str, str]:
    """讀取 wp-config.php 設定"""
    config = {}
    
    if not WP_CONFIG_PATH.exists():
        return config
    
    content = WP_CONFIG_PATH.read_text()
    
    # 解析 define 語句
    pattern = r"define\s*\(\s*['\"](.+?)['\"]\s*,\s*['\"](.+?)['\"]\s*\)"
    matches = re.findall(pattern, content)
    
    for key, value in matches:
        config[key] = value
    
    return config


def show_wp_config():
    """顯示 WordPress 設定"""
    config = get_wp_config()
    
    print("\n" + "=" * 60)
    print("⚙️  WordPress 設定")
    print("=" * 60)
    
    important_keys = [
        'DB_NAME', 'DB_USER', 'DB_HOST', 'DB_CHARSET',
        'WP_DEBUG', 'WP_DEBUG_LOG', 'WP_CACHE'
    ]
    
    for key in important_keys:
        if key in config:
            print(f"  {key}: {config[key]}")


def health_check() -> Dict[str, Any]:
    """WordPress 健康檢查"""
    print("🏥 WordPress 健康檢查...")
    
    health = {
        'wp_version': get_wp_version(),
        'core_integrity': False,
        'plugins_ok': True,
        'themes_ok': True,
        'db_connection': False
    }
    
    # 檢查核心檔案
    check_output = check_core()
    health['core_integrity'] = "Success" in check_output or "success" in check_output.lower()
    
    # 檢查插件更新
    plugins = list_plugins()
    updates_available = [p for p in plugins if p.get('update') == 'available']
    health['plugins_ok'] = len(updates_available) == 0
    
    # 檢查主題更新
    themes = list_themes()
    theme_updates = [t for t in themes if t.get('update') == 'available']
    health['themes_ok'] = len(theme_updates) == 0
    
    # 檢查資料庫連線
    db_check = run_wp_cli(["db", "check"])
    health['db_connection'] = "Success" in db_check or "OK" in db_check
    
    return health


def interactive_cli():
    """交互式 CLI 菜單"""
    while True:
        print("\n" + "=" * 60)
        print("🌐 WordPress Skill - 網站運維管理工具")
        print("=" * 60)
        print("1. 網站資訊")
        print("2. 插件管理")
        print("3. 主題管理")
        print("4. 使用者管理")
        print("5. 文章管理")
        print("6. 搜尋替換")
        print("7. 系統維護")
        print("8. 資料庫操作")
        print("9. 設定管理")
        print("10. 健康檢查")
        print("0. 結束")
        
        choice = input("\n請選擇操作 [0-10]: ").strip()
        
        if choice == '1':
            show_site_info()
            
        elif choice == '2':
            show_plugins()
            action = input("\n操作 [install/activate/deactivate/uninstall/update]: ").strip()
            if action == 'install':
                name = input("插件名稱或路徑: ").strip()
                install_plugin(name)
            elif action == 'activate':
                name = input("插件名稱: ").strip()
                activate_plugin(name)
            elif action == 'deactivate':
                name = input("插件名稱: ").strip()
                deactivate_plugin(name)
            elif action == 'uninstall':
                name = input("插件名稱: ").strip()
                uninstall_plugin(name)
            elif action == 'update':
                update_plugin()
                
        elif choice == '3':
            show_themes()
            action = input("\n操作 [install/activate/delete/update]: ").strip()
            if action == 'install':
                name = input("主題名稱: ").strip()
                install_theme(name)
            elif action == 'activate':
                name = input("主題名稱: ").strip()
                activate_theme(name)
            elif action == 'delete':
                name = input("主題名稱: ").strip()
                delete_theme(name)
            elif action == 'update':
                update_theme()
                
        elif choice == '4':
            show_users()
            action = input("\n操作 [create/delete/update-password/update-role]: ").strip()
            if action == 'create':
                username = input("使用者名: ").strip()
                email = input("郵箱: ").strip()
                role = input("角色 [subscriber/author/editor/administrator]: ").strip() or "subscriber"
                create_user(username, email, role)
            elif action == 'delete':
                user_id = input("使用者 ID: ").strip()
                if user_id:
                    delete_user(int(user_id))
            elif action == 'update-password':
                user_id = input("使用者 ID: ").strip()
                password = input("新密碼: ").strip()
                if user_id and password:
                    update_user_password(int(user_id), password)
            elif action == 'update-role':
                user_id = input("使用者 ID: ").strip()
                role = input("新角色: ").strip()
                if user_id and role:
                    update_user_role(int(user_id), role)
                    
        elif choice == '5':
            show_posts()
            action = input("\n操作 [create/delete]: ").strip()
            if action == 'create':
                title = input("文章標題: ").strip()
                content = input("文章內容: ").strip()
                status = input("狀態 [draft/publish]: ").strip() or "draft"
                create_post(title, content, status)
            elif action == 'delete':
                post_id = input("文章 ID: ").strip()
                if post_id:
                    force = input("強制刪除? (y/n): ").strip().lower() == 'y'
                    delete_post(int(post_id), force=force)
                    
        elif choice == '6':
            search_term = input("搜尋內容: ").strip()
            replace_term = input("替換為: ").strip()
            if search_term and replace_term:
                dry = input("預覽模式? (y/n): ").strip().lower() != 'n'
                output = search_replace(search_term, replace_term, dry_run=dry)
                print(output)
                if dry and input("確認執行? (y/n): ").strip().lower() == 'y':
                    output = search_replace(search_term, replace_term, dry_run=False)
                    print(output)
                    
        elif choice == '7':
            print("\n系統維護:")
            print("  1. 清除緩存")
            print("  2. 刷新重寫規則")
            print("  3. 啟用維護模式")
            print("  4. 關閉維護模式")
            print("  5. 更新 WordPress")
            
            m_choice = input("選擇: ").strip()
            if m_choice == '1':
                flush_cache()
            elif m_choice == '2':
                rewrite_flush()
            elif m_choice == '3':
                run_maintenance_mode(True)
            elif m_choice == '4':
                run_maintenance_mode(False)
            elif m_choice == '5':
                update_core()
                
        elif choice == '8':
            print("\n資料庫操作:")
            print("  1. 導出資料庫")
            print("  2. 導入資料庫")
            
            d_choice = input("選擇: ").strip()
            if d_choice == '1':
                export_database()
            elif d_choice == '2':
                path = input("導入檔案路徑: ").strip()
                if path:
                    import_database(Path(path))
                    
        elif choice == '9':
            show_wp_config()
            
        elif choice == '10':
            health = health_check()
            print("\n健康檢查結果:")
            for k, v in health.items():
                if isinstance(v, bool):
                    status = "✓" if v else "✗"
                    print(f"  {k}: {status}")
                else:
                    print(f"  {k}: {v}")
                    
        elif choice == '0':
            print("再見!")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    interactive_cli()
