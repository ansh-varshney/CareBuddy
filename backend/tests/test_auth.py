"""Tests for authentication routes: register, login, /me."""




# ── Registration ─────────────────────────────────────────────────

def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "pass1234",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "newuser"


def test_register_with_medical_profile(client):
    resp = client.post("/api/auth/register", json={
        "email": "patient@example.com",
        "username": "patient1",
        "password": "pass1234",
        "age": 35,
        "sex": "female",
        "weight_kg": 65.0,
        "height_cm": 168.0,
        "blood_type": "A+",
        "medical_history": "Asthma",
        "allergies": "Penicillin",
        "current_medications": "Salbutamol inhaler",
    })
    assert resp.status_code == 201
    assert "access_token" in resp.json()


def test_register_duplicate_email(client, registered_user):
    resp = client.post("/api/auth/register", json={
        "email": "test@carebuddy.com",   # same as registered_user
        "username": "otheruser",
        "password": "pass1234",
    })
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_register_duplicate_username(client, registered_user):
    resp = client.post("/api/auth/register", json={
        "email": "other@example.com",
        "username": "testuser",          # same as registered_user
        "password": "pass1234",
    })
    assert resp.status_code == 400
    assert "Username already taken" in resp.json()["detail"]


def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={
        "email": "short@example.com",
        "username": "shortpass",
        "password": "abc",               # < 6 chars
    })
    assert resp.status_code == 422


def test_register_invalid_email(client):
    resp = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "username": "userx",
        "password": "pass1234",
    })
    assert resp.status_code == 422


# ── Login ────────────────────────────────────────────────────────

def test_login_success(client, registered_user):
    resp = client.post("/api/auth/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post("/api/auth/login", data={
        "username": registered_user["username"],
        "password": "wrongpassword",
    })
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.json()["detail"]


def test_login_nonexistent_user(client):
    resp = client.post("/api/auth/login", data={
        "username": "ghost",
        "password": "anything",
    })
    assert resp.status_code == 401


# ── Profile (/me) ────────────────────────────────────────────────

def test_get_profile_authenticated(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@carebuddy.com"


def test_get_profile_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_get_profile_includes_medical_fields(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    # Medical fields should be present (None for this test user)
    assert "age" in data
    assert "sex" in data
    assert "blood_type" in data
    assert "medical_history" in data
