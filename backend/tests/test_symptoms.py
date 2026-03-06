"""Tests for the symptom journal endpoints."""

import pytest


def test_list_symptoms_empty(client, auth_headers):
    resp = client.get("/api/symptoms/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_symptom_entry(client, auth_headers):
    resp = client.post("/api/symptoms/", headers=auth_headers, json={
        "symptoms": ["headache", "fever"],
        "description": "Started this morning",
        "severity": 6,
        "body_area": "head",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["symptoms"] == ["headache", "fever"]
    assert data["severity"] == 6
    assert data["body_area"] == "head"


def test_create_symptom_minimal_fields(client, auth_headers):
    """Only symptoms is required."""
    resp = client.post("/api/symptoms/", headers=auth_headers, json={
        "symptoms": ["nausea"],
    })
    assert resp.status_code == 201


def test_create_symptom_invalid_severity(client, auth_headers):
    resp = client.post("/api/symptoms/", headers=auth_headers, json={
        "symptoms": ["pain"],
        "severity": 15,  # > 10, should fail validation
    })
    assert resp.status_code == 422


def test_list_symptoms_after_creation(client, auth_headers):
    client.post("/api/symptoms/", headers=auth_headers, json={"symptoms": ["cough"]})
    client.post("/api/symptoms/", headers=auth_headers, json={"symptoms": ["headache"]})

    resp = client.get("/api/symptoms/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_delete_symptom_entry(client, auth_headers):
    create_resp = client.post("/api/symptoms/", headers=auth_headers,
                              json={"symptoms": ["back pain"]})
    entry_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/symptoms/{entry_id}", headers=auth_headers)
    assert del_resp.status_code in (200, 204)   # 204 No Content is correct REST

    list_resp = client.get("/api/symptoms/", headers=auth_headers)
    assert len(list_resp.json()) == 0


def test_symptoms_require_auth(client):
    resp = client.get("/api/symptoms/")
    assert resp.status_code == 401

    resp = client.post("/api/symptoms/", json={"symptoms": ["pain"]})
    assert resp.status_code == 401
