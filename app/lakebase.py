"""
Lakebase connection helper
"""

import base64
import os
from contextlib import contextmanager
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()

_w = WorkspaceClient()

_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")

def _lakebase_url() -> str:
    try:
        secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
        return base64.b64decode(secret.value).decode("utf-8")
    except Exception:
        return os.getenv("LAKEBASE_URL", "")

@contextmanager
def get_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    url = _lakebase_url()
    if not url:
        raise ValueError("Lakebase URL is not configured")
    conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

def run_query(sql: str, params=None) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def run_write(sql: str, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchall() if cur.description else None