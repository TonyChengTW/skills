# fun3sport WordPress Docker 維運技能集
# 提供完整的 WordPress + MariaDB Docker 維運工具

__version__ = "1.0.0"
__author__ = "fun3sport"

import os
from pathlib import Path

# 載入 .env 檔案
def load_env_file():
    """從 .env 檔案載入環境變數"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 去除可能的引號
                    value = value.strip().strip('"').strip("'")
                    # 只在環境變數不存在時設定
                    if key not in os.environ:
                        os.environ[key] = value

# 載入環境變數
load_env_file()

SKILL_DIR = Path(__file__).parent
PROJECT_DIR = Path(os.getenv("PROJECT_DIR", "/home/fun3sport"))

# 容器名稱 (非敏感資訊)
CONTAINER_WP = "fun3sport_wp"
CONTAINER_DB = "fun3sport_db"
NETWORK_NAME = "fun3sport_net"

# 資料庫設定 (從環境變數讀取敏感資訊)
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
BACKUP_DIR = PROJECT_DIR / os.getenv("BACKUP_DIR", "backups")


def check_sensitive_config():
    """檢查敏感設定是否已正確設定"""
    warnings = []
    
    if DB_CONFIG["password"] == "CHANGE_ME" or not DB_CONFIG["password"]:
        warnings.append("警告: DB_PASSWORD 未設定，請檢查 .env 檔案")
    
    if DB_CONFIG["root_password"] == "CHANGE_ME" or not DB_CONFIG["root_password"]:
        warnings.append("警告: DB_ROOT_PASSWORD 未設定，請檢查 .env 檔案")
    
    if warnings:
        print("\n".join(warnings))
        print(f"\n提示: 複製 {SKILL_DIR / '.env.example'} 到 {SKILL_DIR / '.env'} 並填入真實密碼")
    
    return len(warnings) == 0
