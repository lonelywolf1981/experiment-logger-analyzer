from __future__ import annotations

from app.services.import_service import MAX_UPLOAD_BYTES


def test_import_csv_success(client, experiment_id, sample_csv):
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", sample_csv, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 10
    assert payload["skipped"] == 0
    assert payload["errors"] == 0
    assert payload["filename"] == "data.csv"
    assert "import_run_id" in payload


def test_import_jsonl_success(client, experiment_id, sample_jsonl):
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.jsonl", sample_jsonl, "application/x-jsonlines")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 6
    assert payload["skipped"] == 0
    assert payload["errors"] == 0


def test_import_csv_invalid_header(client, experiment_id):
    csv_content = (
        "channel,timestamp,value,unit,quality,tag\n"
        "TEMP_A,2026-02-28T21:06:00+05:00,3.125,C,OK,temp\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 400
    assert "CSV header must be exactly" in response.json()["detail"]


def test_import_csv_bad_timestamp_counts_as_error(client, experiment_id):
    csv_content = (
        "timestamp,channel,value,unit,quality,tag\n"
        "NOT_A_DATE,TEMP_A,3.125,C,OK,temp\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["errors"] == 1


def test_import_csv_bad_value_counts_as_error(client, experiment_id):
    csv_content = (
        "timestamp,channel,value,unit,quality,tag\n"
        "2026-02-28T21:06:00+05:00,TEMP_A,NOT_A_FLOAT,C,OK,temp\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["errors"] == 1


def test_import_csv_empty_channel_skipped(client, experiment_id):
    csv_content = (
        "timestamp,channel,value,unit,quality,tag\n"
        "2026-02-28T21:06:00+05:00,,3.125,C,OK,temp\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["skipped"] == 1


def test_import_csv_empty_value_skipped(client, experiment_id):
    csv_content = (
        "timestamp,channel,value,unit,quality,tag\n"
        "2026-02-28T21:06:00+05:00,TEMP_A,,C,OK,temp\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["skipped"] == 1


def test_import_csv_invalid_quality_skipped(client, experiment_id):
    csv_content = (
        "timestamp,channel,value,unit,quality,tag\n"
        "2026-02-28T21:06:00+05:00,TEMP_A,3.125,C,UNKNOWN,temp\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["skipped"] == 1


def test_import_experiment_not_found(client):
    response = client.post(
        "/experiments/9999/import",
        files={"file": ("data.csv", "timestamp,channel,value,unit,quality,tag\n", "text/csv")},
    )
    assert response.status_code == 404


def test_import_unsupported_extension(client, experiment_id):
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.txt", "some data", "text/plain")},
    )
    assert response.status_code == 400
    assert "supported" in response.json()["detail"].lower()


def test_import_oversized_file(client, experiment_id):
    oversized = b"x" * (MAX_UPLOAD_BYTES + 1)
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.csv", oversized, "text/csv")},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_import_path_traversal_filename_sanitized(client, experiment_id, sample_csv):
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("../../etc/passwd.csv", sample_csv, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "passwd.csv"


def test_import_jsonl_numeric_value(client, experiment_id):
    """JSONL value как int/float (не строка) корректно записывается."""
    data = '{"timestamp":"2026-02-28T21:06:00+05:00","channel":"V","value":42,"quality":"OK"}\n'
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.jsonl", data, "application/x-jsonlines")},
    )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1


def test_import_jsonl_invalid_json_line_counts_as_error(client, experiment_id):
    data = (
        '{"timestamp":"2026-02-28T21:06:00+05:00","channel":"TEMP_A","value":3.125}\n'
        "not valid json{\n"
        '{"timestamp":"2026-02-28T21:07:00+05:00","channel":"TEMP_A","value":3.2}\n'
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.jsonl", data, "application/x-jsonlines")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 2
    assert payload["errors"] == 1


def test_import_jsonl_empty_lines_ignored(client, experiment_id):
    data = (
        "\n"
        '{"timestamp":"2026-02-28T21:06:00+05:00","channel":"TEMP_A","value":3.125}\n'
        "\n"
        '{"timestamp":"2026-02-28T21:07:00+05:00","channel":"TEMP_A","value":3.2}\n'
        "\n"
    )
    response = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("data.jsonl", data, "application/x-jsonlines")},
    )
    assert response.status_code == 200
    assert response.json()["inserted"] == 2


def test_import_run_linked_to_experiment(client, experiment_id, sample_csv):
    """Импорт привязан к нужному эксперименту."""
    # Создаём второй эксперимент
    other = client.post("/experiments", json={"name": "Other"}).json()["id"]

    r1 = client.post(
        f"/experiments/{experiment_id}/import",
        files={"file": ("a.csv", sample_csv, "text/csv")},
    ).json()
    r2 = client.post(
        f"/experiments/{other}/import",
        files={"file": ("b.csv", sample_csv, "text/csv")},
    ).json()

    # Каналы первого эксперимента не смешиваются со вторым
    ch1 = client.get(f"/experiments/{experiment_id}/channels").json()
    ch2 = client.get(f"/experiments/{other}/channels").json()
    assert len(ch1) == len(ch2)
    assert r1["import_run_id"] != r2["import_run_id"]
