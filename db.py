import duckdb
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("data/learning_hub.duckdb")


def get_connection() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    return con


def init_db() -> None:
    con = get_connection()

    con.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
        """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            provider TEXT,
            resource_type TEXT,
            topic_id INTEGER REFERENCES topics(id),
            difficulty TEXT,
            status TEXT,
            tags TEXT,
            notes TEXT,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed_at TIMESTAMP
        );
        """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            resource_id INTEGER REFERENCES resources(id),
            session_date DATE,
            duration_minutes INTEGER,
            notes TEXT
        );
        """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS technologies (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,  -- 'data_engineering', 'data_science', 'machine_learning'
            current_expertise INTEGER DEFAULT 0,  -- 0-5 scale
            target_expertise INTEGER DEFAULT 5,
            status TEXT DEFAULT 'to_learn',  -- 'to_learn', 'learning', 'mastered'
            priority TEXT DEFAULT 'medium',  -- 'high', 'medium', 'low'
            description TEXT
        );
        """)


def upsert_topic(name: str) -> None:
    con = get_connection()
    con.execute(
        """
        INSERT INTO topics(id, name)
        SELECT COALESCE(MAX(id), 0) + 1, ? FROM topics
        ON CONFLICT(name) DO NOTHING;
        """,
        [name],
    )


def sync_topics_from_config(topic_names: List[str]) -> None:
    for name in topic_names:
        upsert_topic(name)


def get_or_create_topic(name: str) -> Optional[int]:
    if not name:
        return None

    upsert_topic(name)
    con = get_connection()
    row = con.execute("SELECT id FROM topics WHERE name = ?", [name]).fetchone()
    return int(row[0]) if row else None


def resource_exists(url: str, title: str) -> bool:
    con = get_connection()
    row = con.execute(
        "SELECT 1 FROM resources WHERE LOWER(url) = LOWER(?) OR LOWER(title) = LOWER(?) LIMIT 1",
        [url or "", title or ""],
    ).fetchone()
    return row is not None


def sync_resources_from_json(json_path: Path) -> tuple[int, int]:
    if not json_path.exists():
        return 0, 0

    with json_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    resources = []
    if isinstance(payload, dict):
        resources = payload.get("resources", [])
    elif isinstance(payload, list):
        resources = payload

    inserted = 0
    skipped = 0

    for item in resources:
        title = item.get("title")
        url = item.get("url")
        if not title or not url:
            continue

        if resource_exists(url, title):
            skipped += 1
            continue

        topic_id = get_or_create_topic(item.get("topic")) if item.get("topic") else None
        insert_resource(
            {
                "title": title,
                "url": url,
                "provider": item.get("provider"),
                "resource_type": item.get("resource_type"),
                "topic_id": topic_id,
                "difficulty": item.get("difficulty"),
                "status": item.get("status"),
                "tags": item.get("tags"),
                "notes": item.get("notes"),
                "rating": item.get("rating"),
            }
        )
        inserted += 1

    return inserted, skipped


def list_topics() -> List[Dict[str, Any]]:
    con = get_connection()
    return con.execute("SELECT id, name FROM topics ORDER BY name").fetchall()


def insert_resource(data: Dict[str, Any]) -> None:
    con = get_connection()
    con.execute(
        """
        INSERT INTO resources (
            id, title, url, provider, resource_type, topic_id,
            difficulty, status, tags, notes, rating
        )
        SELECT COALESCE(MAX(id), 0) + 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        FROM resources;
        """,
        [
            data.get("title"),
            data.get("url"),
            data.get("provider"),
            data.get("resource_type"),
            data.get("topic_id"),
            data.get("difficulty"),
            data.get("status"),
            data.get("tags"),
            data.get("notes"),
            data.get("rating"),
        ],
    )


def update_resource_status(resource_id: int, new_status: str) -> None:
    con = get_connection()
    con.execute(
        "UPDATE resources SET status = ?, last_accessed_at = CURRENT_TIMESTAMP WHERE id = ?",
        [new_status, resource_id],
    )


def update_last_accessed(resource_id: int) -> None:
    con = get_connection()
    con.execute(
        "UPDATE resources SET last_accessed_at = CURRENT_TIMESTAMP WHERE id = ?",
        [resource_id],
    )


def list_resources(
    topic_ids: Optional[List[int]] = None,
    providers: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    search_text: Optional[str] = None,
):
    con = get_connection()

    base_query = """
        SELECT r.id, r.title, r.url, r.provider, r.resource_type,
               t.name AS topic, r.difficulty, r.status, r.tags,
               r.notes, r.rating, r.created_at, r.last_accessed_at
        FROM resources r
        LEFT JOIN topics t ON r.topic_id = t.id
        WHERE 1=1
    """

    params: List[Any] = []

    if topic_ids:
        placeholders = ",".join(["?"] * len(topic_ids))
        base_query += f" AND r.topic_id IN ({placeholders})"
        params.extend(topic_ids)

    if providers:
        placeholders = ",".join(["?"] * len(providers))
        base_query += f" AND r.provider IN ({placeholders})"
        params.extend(providers)

    if statuses:
        placeholders = ",".join(["?"] * len(statuses))
        base_query += f" AND r.status IN ({placeholders})"
        params.extend(statuses)

    if search_text:
        base_query += " AND (LOWER(r.title) LIKE ? OR LOWER(r.tags) LIKE ?)"
        like = f"%{search_text.lower()}%"
        params.extend([like, like])

    base_query += " ORDER BY r.created_at DESC"

    return con.execute(base_query, params).df()


def insert_session(data: Dict[str, Any]) -> None:
    con = get_connection()
    con.execute(
        """
        INSERT INTO sessions (
            id, resource_id, session_date, duration_minutes, notes
        )
        SELECT COALESCE(MAX(id), 0) + 1, ?, ?, ?, ?
        FROM sessions;
        """,
        [
            data.get("resource_id"),
            data.get("session_date"),
            data.get("duration_minutes"),
            data.get("notes"),
        ],
    )


def list_sessions():
    con = get_connection()
    return con.execute("""
        SELECT s.id, s.session_date, s.duration_minutes, s.notes,
               r.title AS resource_title
        FROM sessions s
        LEFT JOIN resources r ON s.resource_id = r.id
        ORDER BY s.session_date DESC, s.id DESC
        """).df()


def upsert_technology(name: str, category: str, priority: str, description: str) -> None:
    con = get_connection()
    con.execute(
        """
        INSERT INTO technologies(id, name, category, priority, description)
        SELECT COALESCE(MAX(id), 0) + 1, ?, ?, ?, ?
        FROM technologies
        ON CONFLICT(name) DO UPDATE SET
            category = excluded.category,
            priority = excluded.priority,
            description = excluded.description;
        """,
        [name, category, priority, description],
    )


def sync_technologies_from_config(tech_config: Dict) -> None:
    for category, techs in tech_config.items():
        for tech in techs:
            upsert_technology(tech["name"], category, tech.get("priority", "medium"), tech.get("description", ""))


def list_technologies() -> List[Dict[str, Any]]:
    con = get_connection()
    return (
        con.execute(
            "SELECT id, name, category, current_expertise, target_expertise, status, priority, description FROM technologies ORDER BY category, priority DESC, name"
        )
        .df()
        .to_dict("records")
    )


def update_technology_expertise(tech_id: int, current_expertise: int, status: str) -> None:
    con = get_connection()
    con.execute(
        "UPDATE technologies SET current_expertise = ?, status = ? WHERE id = ?",
        [current_expertise, status, tech_id],
    )
