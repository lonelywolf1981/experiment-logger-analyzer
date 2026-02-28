from __future__ import annotations

from app.services.export_service import MAX_EXPORT_ROWS


def test_export_csv_returns_csv(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(f"/experiments/{experiment_id}/export.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    lines = response.text.strip().splitlines()
    # header + 10 rows
    assert len(lines) == 11
    assert lines[0] == "timestamp,channel,value,unit,quality,tag"


def test_export_csv_not_found(client):
    response = client.get("/experiments/9999/export.csv")
    assert response.status_code == 404


def test_export_csv_channel_filter(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(
        f"/experiments/{experiment_id}/export.csv",
        params={"channels": "TEMP_A"},
    )
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    # header + 4 TEMP_A rows
    assert len(lines) == 5
    for line in lines[1:]:
        assert line.split(",")[1] == "TEMP_A"


def test_export_csv_multiple_channels(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(
        f"/experiments/{experiment_id}/export.csv",
        params=[("channels", "TEMP_A"), ("channels", "PRESS_1")],
    )
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    # header + 4 TEMP_A + 2 PRESS_1
    assert len(lines) == 7


def test_export_csv_quality_filter(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(
        f"/experiments/{experiment_id}/export.csv",
        params={"quality": "WARN"},
    )
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    # header + 1 WARN row
    assert len(lines) == 2


def test_export_csv_content_disposition_header(client, experiment_id, sample_csv):
    client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    response = client.get(f"/experiments/{experiment_id}/export.csv")
    assert "attachment" in response.headers.get("content-disposition", "")


def test_export_max_rows_constant_defined():
    assert MAX_EXPORT_ROWS == 5000
