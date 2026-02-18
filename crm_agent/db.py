import sqlite3
from typing import Dict, List, Any, Set
from .config import DB_PATH

BLOCKED: Set[str] = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "REPLACE"}

def get_schema() -> str:
    """Retrieve the database schema for all tables."""
    c = sqlite3.connect(DB_PATH)
    r = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL").fetchall()
    c.close()
    return "\n\n".join(x[0] for x in r)

def run_sql_query(sql: str) -> Dict[str, Any]:
    """Execute a read-only SQL query and return results.
    
    Args:
        sql: SQL query string to execute
        
    Returns:
        Dictionary with status, columns, rows, and row_count on success
        or status and error message on failure
    """
    u = sql.strip().upper()
    for kw in BLOCKED:
        if u.startswith(kw):
            return {"status": "error", "error": f"Blocked: {kw}"}
    try:
        c = sqlite3.connect(DB_PATH)
        cur = c.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows: List[List[Any]] = [list(r) for r in cur.fetchall()]
        c.close()
        return {"status": "success", "columns": cols, "rows": rows, "row_count": len(rows)}
    except Exception as e:
        return {"status": "error", "error": str(e)}
