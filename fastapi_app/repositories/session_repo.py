import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Protocol, List, Dict, Any, Tuple

class SessionRepositoryProtocol(Protocol):
    def get_sessions(self, limit: int, offset: int, search: str, track: str, day: str, tz: str) -> Tuple[int, List[Dict[str, Any]]]: ...
    def get_session_by_id(self, session_id: str) -> Dict[str, Any]: ...

class PostgresSessionRepository:
    def _connect(self):
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME'), user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'), host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT', '5432'), cursor_factory=RealDictCursor
        )

    def get_sessions(self, limit: int, offset: int, search: str, track: str, day: str, tz: str) -> Tuple[int, List[Dict[str, Any]]]:
        where_clauses = ["1=1"]
        params = {'limit': limit, 'offset': offset}

        if search:
            where_clauses.append("(s.title ILIKE %(search)s OR s.description ILIKE %(search)s)")
            params['search'] = f"%{search}%"
        if track:
            where_clauses.append("s.track_id = %(track)s")
            params['track'] = track
            
        if day and tz:
            where_clauses.append("DATE(s.start_time AT TIME ZONE %(tz)s) = %(day)s::DATE")
            params['day'] = day
            params['tz'] = tz

        where_str = " AND ".join(where_clauses)
        count_sql = f"SELECT COUNT(*) as total FROM content.session s WHERE {where_str};"
        
        data_sql = f"""
            SELECT 
                s.id, s.title, s.description AS abstract, s.start_time AS starts_at, s.end_time AS ends_at, s.capacity,
                CASE WHEN t.id IS NOT NULL THEN json_build_object('id', t.id, 'name', t.name) ELSE NULL END AS track,
                COALESCE(
                    (SELECT json_agg(
                        json_build_object('id', sp.id, 'name', sp.name)
                    )
                    FROM content.session_speaker ssp
                    JOIN content.speaker sp ON ssp.speaker_id = sp.id
                    WHERE ssp.session_id = s.id), 
                    '[]'::json
                ) AS speakers
            FROM content.session s 
            LEFT JOIN content.track t ON s.track_id = t.id
            WHERE {where_str} 
            ORDER BY s.start_time ASC 
            LIMIT %(limit)s OFFSET %(offset)s;
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()['total']
            cur.execute(data_sql, params)
            return total, cur.fetchall()
        
    def get_session_by_id(self, session_id: str) -> Dict[str, Any]:
        sql = """
            SELECT 
                s.id, s.title, s.description AS abstract, s.start_time AS starts_at, s.end_time AS ends_at, s.capacity,
                CASE WHEN t.id IS NOT NULL THEN json_build_object('id', t.id, 'name', t.name) ELSE NULL END AS track,
                COALESCE(
                    (SELECT json_agg(
                        json_build_object('id', sp.id, 'name', sp.name)
                    )
                    FROM content.session_speaker ssp
                    JOIN content.speaker sp ON ssp.speaker_id = sp.id
                    WHERE ssp.session_id = s.id), 
                    '[]'::json
                ) AS speakers
            FROM content.session s 
            LEFT JOIN content.track t ON s.track_id = t.id
            WHERE s.id = %(session_id)s;
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, {'session_id': session_id})
            return cur.fetchone()