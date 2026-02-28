from __future__ import annotations

import pytest


def test_channels_empty_experiment(client, experiment_id):
    response = client.get(f"/experiments/{experiment_id}/channels")
    assert response.status_code == 200
    assert response.json() == []


def test_channels_not_found(client):
    response = client.get("/experiments/9999/channels")
    assert response.status_code == 404


def test_channels_returns_stats(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(f"/experiments/{experiment_id}/channels")
    assert response.status_code == 200
    channels = response.json()

    # sample_csv содержит 5 каналов: POWER_1, PRESS_1, STATE, TEMP_A, TEMP_B
    assert len(channels) == 5

    temp_a = next(ch for ch in channels if ch["channel"] == "TEMP_A")
    assert temp_a["count"] == 4
    assert temp_a["min"] == pytest.approx(3.125)
    assert temp_a["max"] == pytest.approx(3.450)
    assert temp_a["first_ts"] is not None
    assert temp_a["last_ts"] is not None


def test_channels_ordered_alphabetically(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    channels = client.get(f"/experiments/{experiment_id}/channels").json()
    names = [ch["channel"] for ch in channels]
    assert names == sorted(names)


def test_series_empty_channels(client, experiment_id):
    response = client.get(f"/experiments/{experiment_id}/series")
    assert response.status_code == 200
    assert response.json() == {}


def test_series_not_found(client):
    response = client.get("/experiments/9999/series")
    assert response.status_code == 404


def test_series_single_channel(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(
        f"/experiments/{experiment_id}/series",
        params={"channels": "TEMP_A"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "TEMP_A" in data
    assert len(data["TEMP_A"]) == 4
    for point in data["TEMP_A"]:
        assert "timestamp" in point
        assert "value" in point


def test_series_multiple_channels(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(
        f"/experiments/{experiment_id}/series",
        params=[("channels", "TEMP_A"), ("channels", "PRESS_1")],
    )
    assert response.status_code == 200
    data = response.json()
    assert "TEMP_A" in data
    assert "PRESS_1" in data
    assert len(data["TEMP_A"]) == 4
    assert len(data["PRESS_1"]) == 2


def test_series_unknown_channel_returns_empty_list(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(
        f"/experiments/{experiment_id}/series",
        params={"channels": "NONEXISTENT"},
    )
    assert response.status_code == 200
    assert response.json()["NONEXISTENT"] == []


def test_series_time_filter(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    # Берём только точки до 21:07 — должна остаться 1 точка TEMP_A
    response = client.get(
        f"/experiments/{experiment_id}/series",
        params={
            "channels": "TEMP_A",
            "end": "2026-02-28T21:07:00+05:00",
        },
    )
    assert response.status_code == 200
    data = response.json()["TEMP_A"]
    # Включает 21:06 и 21:07 → 2 точки
    assert len(data) == 2


def test_summary_empty_experiment(client, experiment_id):
    response = client.get(f"/experiments/{experiment_id}/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_points"] == 0
    assert summary["channels_count"] == 0
    assert summary["duration_seconds"] is None
    assert summary["first_ts"] is None
    assert summary["last_ts"] is None


def test_summary_not_found(client):
    response = client.get("/experiments/9999/summary")
    assert response.status_code == 404


def test_summary_with_data(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(f"/experiments/{experiment_id}/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_points"] == 10
    assert summary["channels_count"] == 5
    assert summary["duration_seconds"] is not None
    assert summary["duration_seconds"] > 0
    assert "first_ts" in summary
    assert "last_ts" in summary


def test_summary_points_by_quality(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    summary = client.get(f"/experiments/{experiment_id}/summary").json()
    # sample_csv имеет 9 OK и 1 WARN
    assert summary["points_by_quality"]["OK"] == 9
    assert summary["points_by_quality"]["WARN"] == 1


