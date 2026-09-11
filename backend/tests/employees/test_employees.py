def test_create_and_list_employees(client, auth_headers):
    # 1. Create employee
    payload = {
        "employee_code": "EMP-999",
        "first_name": "Test",
        "last_name": "Developer",
        "email": "dev@test.corp",
        "designation": "Backend Engineer",
        "status": "ACTIVE"
    }
    resp = client.post("/api/v1/employees", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    emp_data = resp.get_json()["data"]
    assert emp_data["employee_code"] == "EMP-999"
    emp_id = emp_data["id"]

    # 2. List employees
    list_resp = client.get("/api/v1/employees", headers=auth_headers)
    assert list_resp.status_code == 200
    items = list_resp.get_json()["data"]["items"]
    assert any(e["id"] == emp_id for e in items)

    # 3. Update employee
    update_resp = client.put(f"/api/v1/employees/{emp_id}", json={"designation": "Lead Engineer"}, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.get_json()["data"]["designation"] == "Lead Engineer"

    # 4. Deactivate employee
    del_resp = client.delete(f"/api/v1/employees/{emp_id}", headers=auth_headers)
    assert del_resp.status_code == 200
