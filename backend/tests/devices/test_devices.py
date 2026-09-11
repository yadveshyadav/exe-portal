from app.models.device import Device
from app.models.company import Company
from app.extensions import db

def test_list_and_update_device(client, auth_headers):
    # Insert test device
    company = Company.query.first()
    dev = Device(
        company_id=company.id,
        device_uid="TEST-DEVICE-UID-123",
        hostname="WS-TEST-01",
        status="ONLINE"
    )
    db.session.add(dev)
    db.session.commit()

    # List devices
    resp = client.get("/api/v1/devices", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.get_json()["data"]["items"]
    assert any(d["device_uid"] == "TEST-DEVICE-UID-123" for d in items)

    # Get device detail
    detail_resp = client.get(f"/api/v1/devices/{dev.id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.get_json()["data"]["hostname"] == "WS-TEST-01"

    # Update device
    up_resp = client.put(f"/api/v1/devices/{dev.id}", json={"hostname": "WS-TEST-RENAMED"}, headers=auth_headers)
    assert up_resp.status_code == 200
    assert up_resp.get_json()["data"]["hostname"] == "WS-TEST-RENAMED"
