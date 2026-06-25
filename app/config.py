import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env', override=False)


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
