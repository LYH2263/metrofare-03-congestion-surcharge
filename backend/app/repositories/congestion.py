import sqlite3

from app.modules.congestion_surcharge import surcharge_for_level, validate_level


def _canonical(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def edge_exists(conn: sqlite3.Connection, a: str, b: str) -> bool:
    x, y = _canonical(a, b)
    row = conn.execute("SELECT 1 FROM edges WHERE a=? AND b=? OR a=? AND b=?", (x, y, y, x)).fetchone()
    return row is not None


def upsert(conn: sqlite3.Connection, a: str, b: str, level: str) -> dict:
    validate_level(level)
    if not edge_exists(conn, a, b):
        from app.modules.congestion_surcharge import CongestionError

        raise CongestionError(f"edge not found: {a}-{b}")
    x, y = _canonical(a, b)
    amount = surcharge_for_level(level)
    conn.execute(
        """
        INSERT INTO edge_congestion(a, b, level, surcharge)
        VALUES (?,?,?,?)
        ON CONFLICT(a,b) DO UPDATE SET level=excluded.level, surcharge=excluded.surcharge
        """,
        (x, y, level, amount),
    )
    conn.commit()
    return {"a": x, "b": y, "level": level, "surcharge": amount}


def delete(conn: sqlite3.Connection, a: str, b: str) -> None:
    x, y = _canonical(a, b)
    conn.execute("DELETE FROM edge_congestion WHERE a=? AND b=?", (x, y))
    conn.commit()


def list_all(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT a,b,level,surcharge FROM edge_congestion ORDER BY a,b").fetchall()
    return [dict(r) for r in rows]
