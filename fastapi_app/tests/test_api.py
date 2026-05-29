import pytest
import os
import uuid
import psycopg2
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="function")
def db_integration_setup():
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'), user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'), host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT', '5432')
    )
    cur = conn.cursor()

    conf_id = str(uuid.uuid4())
    track_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    speaker_id = str(uuid.uuid4())
    ss_id = str(uuid.uuid4())
    
    now = datetime.now(timezone.utc)

    cur.execute(
        "INSERT INTO content.conference (id, name, start_date, end_date, created, modified) VALUES (%s, %s, %s, %s, %s, %s)",
        (conf_id, "Conf de Prueba", now, now, now, now)
    )

    cur.execute(
        "INSERT INTO content.track (id, conference_id, name, created, modified) VALUES (%s, %s, %s, %s, %s)",
        (track_id, conf_id, "Track de Integración", now, now)
    )

    cur.execute(
        "INSERT INTO content.speaker (id, name, email, created, modified) VALUES (%s, %s, %s, %s, %s)",
        (speaker_id, "Speaker Test", f"test_{speaker_id}@test.com", now, now)
    )
    
    cur.execute("""
        INSERT INTO content.session (id, track_id, title, description, start_time, end_time, capacity, created, modified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        session_id, track_id, "Sesión de Prueba Real", "Abstract", 
        datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc), 
        datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc), 
        100, now, now
    ))

    cur.execute(
        "INSERT INTO content.session_speaker (id, session_id, speaker_id, created, modified) VALUES (%s, %s, %s, %s, %s)",
        (ss_id, session_id, speaker_id, now, now)
    )
    
    conn.commit()

    yield session_id

    cur.execute("DELETE FROM content.session_speaker WHERE id = %s", (ss_id,))
    cur.execute("DELETE FROM content.session WHERE id = %s", (session_id,))
    cur.execute("DELETE FROM content.speaker WHERE id = %s", (speaker_id,))
    cur.execute("DELETE FROM content.track WHERE id = %s", (track_id,))
    cur.execute("DELETE FROM content.conference WHERE id = %s", (conf_id,))
    conn.commit()
    
    cur.close()
    conn.close()

def test_healthz_endpoint():
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200

def test_get_session_detail_real_db(db_integration_setup):
    """
    Prueba que la consulta SQL con json_build_object y json_agg funciona en Postgres.
    """
    session_id = db_integration_setup

    response = client.get(f"/api/v1/sessions/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Sesión de Prueba Real"
    assert data["track"]["name"] == "Track de Integración"
    assert data["speakers"][0]["name"] == "Speaker Test"

def test_search_sessions_real_db(db_integration_setup):
    """
    Prueba del endpoint de búsqueda
    """
    response = client.get("/api/v1/sessions/search/?query=Prueba Real")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["title"] == "Sesión de Prueba Real" for s in data)

def test_timezone_aware_filtering_real_db(db_integration_setup):
    """
    Prueba obligatoria: Valida que la función AT TIME ZONE de Postgres filtra correctamente.
    La sesión se insertó el 2026-07-01 a las 09:00 UTC.
    Para la zona America/La_Paz (UTC-4), ocurre el mismo día a las 05:00 AM.
    """
    response = client.get("/api/v1/sessions/?day=2026-07-01&tz=America/La_Paz")
    
    assert response.status_code == 200
    data = response.json()
    
    assert any(s["title"] == "Sesión de Prueba Real" for s in data["results"])

def test_pagination_validation_error():
    """Valida la restricción de Pydantic."""
    response = client.get("/api/v1/sessions/?page=0")
    assert response.status_code == 422