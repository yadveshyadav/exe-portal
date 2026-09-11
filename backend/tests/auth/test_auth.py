def test_login_success(client, db_session):
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "testadmin",
        "password": "Admin@123456"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["username"] == "testadmin"

def test_login_invalid_password(client, db_session):
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "testadmin",
        "password": "WrongPassword123"
    })
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["success"] is False

def test_get_current_user_profile(client, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["username"] == "testadmin"
