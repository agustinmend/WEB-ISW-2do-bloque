import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Protocol, List, Dict, Any

class TrackRepositoryProtocol(Protocol):
    def get_tracks(self) -> List[Dict[str, Any]]: ...

class PostgresTrackRepository:
    def _connect(self):
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME'), user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'), host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT', '5432'), cursor_factory=RealDictCursor
        )

    def get_tracks(self) -> List[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, name, description FROM content.track ORDER BY name")
            return cur.fetchall()