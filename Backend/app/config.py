import json
import os
from pathlib import Path

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Try Backend root first (.env sits at Backend/.env), then project root
_env_file = Path(__file__).resolve().parent.parent / '.env'
if not _env_file.exists():
    _env_file = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(_env_file, override=False)


BASE_DIR = Path(__file__).resolve().parent.parent


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def get_mysql_url() -> str:
    host = get_env('DB_HOST', 'localhost')
    port = get_env('DB_PORT', '3306')
    user = get_env('DB_USER', 'root')
    password = get_env('DB_PASSWORD', '')
    database = get_env('DB_NAME', 'cv')
    return f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'


def get_geocoder_user_agent() -> str:
    return get_env('GEOCODER_USER_AGENT', 'resume_analyzer/1.0')


def get_field_rules() -> dict:
    rules_path = Path(__file__).with_name('field_rules.json')
    with rules_path.open('r', encoding='utf-8') as fh:
        return json.load(fh)


def get_extractor_provider() -> str:
    """Returns the active V1 extractor strategy: 'auto', 'custom_rule', or 'gemini'."""
    return get_env('EXTRACTOR_PROVIDER', 'auto')


def get_max_upload_size_mb() -> float:
    """Returns the maximum upload size limit in MB."""
    try:
        return float(get_env('MAX_UPLOAD_SIZE_MB', '5.0'))
    except ValueError:
        return 5.0
