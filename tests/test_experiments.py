from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_experiment(client: TestClient):
    response = client.post(
        "/experiments",
        json={"name": "Exp 1", "stand": "bench-1", "operator": "Alice", "notes": "test run"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Exp 1"
    assert payload["stand"] == "bench-1"
    assert payload["operator"] == "Alice"
    assert payload["notes"] == "test run"
    assert "id" in payload
    assert "created_at" in payload


def test_create_experiment_minimal(client: TestClient):
    """Только name обязательно, остальные поля опциональны."""
    response = client.post("/experiments", json={"name": "Minimal"})
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Minimal"
    assert payload["stand"] is None
    assert payload["operator"] is None
    assert payload["notes"] is None


def test_create_experiment_blank_name_rejected(client: TestClient):
    response = client.post("/experiments", json={"name": "   "})
    assert response.status_code == 422


def test_list_experiments_empty(client: TestClient):
    response = client.get("/experiments")
    assert response.status_code == 200
    assert response.json() == []


def test_list_experiments_ordered_newest_first(client: TestClient):
    client.post("/experiments", json={"name": "First"})
    client.post("/experiments", json={"name": "Second"})
    client.post("/experiments", json={"name": "Third"})

    response = client.get("/experiments")
    assert response.status_code == 200
    names = [e["name"] for e in response.json()]
    assert names[0] == "Third"
    assert names[-1] == "First"


def test_get_experiment(client: TestClient, experiment_id: int):
    response = client.get(f"/experiments/{experiment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == experiment_id


def test_get_experiment_not_found(client: TestClient):
    response = client.get("/experiments/9999")
    assert response.status_code == 404


def test_delete_experiment(client: TestClient, experiment_id: int):
    response = client.delete(f"/experiments/{experiment_id}")
    assert response.status_code == 204

    # Проверяем что эксперимент удалён
    response = client.get(f"/experiments/{experiment_id}")
    assert response.status_code == 404


def test_delete_experiment_not_found(client: TestClient):
    response = client.delete("/experiments/9999")
    assert response.status_code == 404


def test_delete_experiment_cascades_data(client: TestClient, experiment_id: int, sample_csv: str):
    """При удалении эксперимента DataPoints и ImportRun удаляются каскадно."""
    # Импортируем данные
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("events.csv", sample_csv, "text/csv")},
    )
    # Проверяем что есть каналы
    channels_resp = client.get(f"/experiments/{experiment_id}/channels")
    assert channels_resp.status_code == 200
    assert len(channels_resp.json()) > 0

    # Удаляем эксперимент
    client.delete(f"/experiments/{experiment_id}")

    # После удаления каналы недоступны (404)
    response = client.get(f"/experiments/{experiment_id}/channels")
    assert response.status_code == 404
