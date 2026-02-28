from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.dependencies import get_db
from app.main import app
from app.models import Base


@pytest.fixture()
def sample_csv() -> str:
    """CSV с 10 точками по 4 каналам для повторного использования в тестах."""
    return (
        "timestamp,channel,value,unit,quality,tag\n"
        "2026-02-28T21:05:10+05:00,STATE,1,,OK,experiment\n"
        "2026-02-28T21:06:00+05:00,TEMP_A,3.125,C,OK,temp\n"
        "2026-02-28T21:06:00+05:00,TEMP_B,3.081,C,OK,temp\n"
        "2026-02-28T21:06:00+05:00,PRESS_1,1.023,bar,OK,pressure\n"
        "2026-02-28T21:07:00+05:00,TEMP_A,3.142,C,OK,temp\n"
        "2026-02-28T21:07:00+05:00,TEMP_B,3.090,C,OK,temp\n"
        "2026-02-28T21:08:00+05:00,TEMP_A,3.450,C,WARN,temp\n"
        "2026-02-28T21:08:30+05:00,PRESS_1,1.031,bar,OK,pressure\n"
        "2026-02-28T21:10:05+05:00,POWER_1,420.500,W,OK,power\n"
        "2026-02-28T21:10:30+05:00,TEMP_A,3.220,C,OK,temp\n"
    )


@pytest.fixture()
def sample_jsonl() -> str:
    """JSONL с 6 точками для повторного использования в тестах."""
    return (
        '{"timestamp":"2026-02-28T21:05:10+05:00","channel":"STATE","value":1,"quality":"OK","tag":"experiment"}\n'
        '{"timestamp":"2026-02-28T21:06:00+05:00","channel":"TEMP_A","value":3.125,"unit":"C","quality":"OK","tag":"temp"}\n'
        '{"timestamp":"2026-02-28T21:06:00+05:00","channel":"TEMP_B","value":3.081,"unit":"C","quality":"OK","tag":"temp"}\n'
        '{"timestamp":"2026-02-28T21:06:00+05:00","channel":"PRESS_1","value":1.023,"unit":"bar","quality":"OK","tag":"pressure"}\n'
        '{"timestamp":"2026-02-28T21:10:05+05:00","channel":"POWER_1","value":420.5,"unit":"W","quality":"OK","tag":"power"}\n'
        '{"timestamp":"2026-02-28T21:12:00+05:00","channel":"STATE","value":0,"quality":"OK","tag":"experiment"}\n'
    )


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def experiment_id(client: TestClient) -> int:
    """Создаёт эксперимент и возвращает его id для использования в тестах."""
    response = client.post(
        "/experiments",
        json={"name": "Test Experiment", "stand": "stand-01", "operator": "tester"},
    )
    assert response.status_code == 201
    return response.json()["id"]
