import pytest
import json
from datetime import datetime, timezone
from app.models.device import Device
from app.models.agent import Agent
from app.models.company import Company
from app.models.employee import Employee
from app.models.audit_log import AuditLog
from app.extensions import db
from app.services.presence_service import PresenceService

def test_agent_registration_new_device(client, db_session):
    """Test POST /api/v1/agents/register creates unassigned device in REGISTERED status."""
    payload = {
        "device_id": "WIN-UUID-TEST-001",
        "hostname": "PC-TEST-001",
        "operating_system": "Windows 11 Enterprise (23H2)",
        "agent_version": "1.0.0",
        "company_code": "TEST_CORP"
    }

    resp = client.post("/api/v1/agents/register", json=payload)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["success"] is True
    assert body["device"]["hostname"] == "PC-TEST-001"
    assert body["device"]["status"] == "REGISTERED"
    assert body["device"]["device_id"] == "WIN-UUID-TEST-001"

    # Verify in DB
    db.session.expire_all()
    dev = Device.query.filter_by(device_uuid="WIN-UUID-TEST-001").first()
    assert dev is not None
    assert dev.employee_id is None # Unassigned by default
    assert dev.status == "REGISTERED"
    assert dev.agent_version == "1.0.0"

    # Verify Redis presence state
    presence = PresenceService.get_device_presence("WIN-UUID-TEST-001")
    assert presence is not None
    assert presence["status"] == "REGISTERED"
    assert presence["hostname"] == "PC-TEST-001"

def test_agent_registration_duplicate_upsert(client, db_session):
    """Test re-registering the same agent updates metadata without duplicating record."""
    payload = {
        "device_id": "WIN-UUID-TEST-002",
        "hostname": "PC-ORIGINAL",
        "operating_system": "Windows 10 Pro",
        "agent_version": "1.0.0",
        "company_code": "TEST_CORP"
    }
    resp1 = client.post("/api/v1/agents/register", json=payload)
    assert resp1.status_code == 201

    # Re-register with updated hostname and OS
    update_payload = {
        "device_id": "WIN-UUID-TEST-002",
        "hostname": "PC-RENAMED",
        "operating_system": "Windows 11 Pro",
        "agent_version": "1.0.1",
        "company_code": "TEST_CORP"
    }
    resp2 = client.post("/api/v1/agents/register", json=update_payload)
    assert resp2.status_code == 200
    body = resp2.get_json()
    assert body["device"]["hostname"] == "PC-RENAMED"

    # Ensure no duplicates in DB
    db.session.expire_all()
    count = Device.query.filter_by(device_uuid="WIN-UUID-TEST-002").count()
    assert count == 1
    dev = Device.query.filter_by(device_uuid="WIN-UUID-TEST-002").first()
    assert dev.hostname == "PC-RENAMED"
    assert dev.agent_version == "1.0.1"

def test_agent_registration_disabled_device_rejected(client, db_session):
    """Test disabled device cannot re-register."""
    company = Company.query.first()
    dev = Device(
        company_id=company.id,
        device_uuid="WIN-UUID-DISABLED",
        hostname="PC-DISABLED",
        status="DISABLED"
    )
    db.session.add(dev)
    db.session.commit()

    payload = {
        "device_id": "WIN-UUID-DISABLED",
        "hostname": "PC-DISABLED",
        "agent_version": "1.0.0"
    }
    resp = client.post("/api/v1/agents/register", json=payload)
    assert resp.status_code == 403
    assert "disabled" in resp.get_json()["message"].lower()

def test_agent_heartbeat_lifecycle(client, db_session):
    """Test agent heartbeat transitions device to ONLINE and updates presence."""
    # Register first
    reg_payload = {
        "device_id": "WIN-UUID-HB-001",
        "hostname": "PC-HB-001",
        "operating_system": "Windows 11",
        "agent_version": "1.0.0"
    }
    client.post("/api/v1/agents/register", json=reg_payload)

    # Send Heartbeat
    hb_payload = {
        "device_id": "WIN-UUID-HB-001",
        "timestamp": "2026-08-23T07:30:00Z",
        "agent_version": "1.0.0",
        "status": "ONLINE"
    }
    hb_resp = client.post("/api/v1/agents/heartbeat", json=hb_payload)
    assert hb_resp.status_code == 200
    hb_data = hb_resp.get_json()
    assert hb_data["success"] is True
    assert hb_data["data"]["status"] == "ACK"

    # Verify device status is now ONLINE
    db.session.expire_all()
    dev = Device.query.filter_by(device_uuid="WIN-UUID-HB-001").first()
    assert dev.status == "ONLINE"
    assert dev.last_seen_at is not None

    # Verify Redis presence updated
    presence = PresenceService.get_device_presence("WIN-UUID-HB-001")
    assert presence is not None
    assert presence["status"] == "ONLINE"

def test_agent_heartbeat_version_change_audit(client, db_session):
    """Test agent heartbeat with changed version records audit log."""
    reg_payload = {
        "device_id": "WIN-UUID-VERSION-001",
        "hostname": "PC-VER-001",
        "agent_version": "1.0.0"
    }
    client.post("/api/v1/agents/register", json=reg_payload)

    # Send Heartbeat with upgraded version 2.0.0
    hb_payload = {
        "device_id": "WIN-UUID-VERSION-001",
        "agent_version": "2.0.0",
        "status": "ONLINE"
    }
    hb_resp = client.post("/api/v1/agents/heartbeat", json=hb_payload)
    assert hb_resp.status_code == 200

    db.session.expire_all()
    dev = Device.query.filter_by(device_uuid="WIN-UUID-VERSION-001").first()
    assert dev.agent_version == "2.0.0"

    # Check audit log
    log = AuditLog.query.filter_by(action="AGENT_VERSION_CHANGED", resource_id=dev.id).first()
    assert log is not None
    assert log.after_value["agent_version"] == "2.0.0"

def test_devices_list_and_filters(client, auth_headers, db_session):
    """Test GET /api/v1/devices filtering by status, search, and unassigned."""
    company = Company.query.first()
    
    # Create employee
    emp = Employee(
        company_id=company.id,
        employee_code="EMP-100",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@test.corp"
    )
    db.session.add(emp)
    db.session.flush()

    # Assigned device
    dev1 = Device(
        company_id=company.id,
        device_uuid="WIN-DEV-ASSIGNED",
        hostname="PC-JANE-01",
        employee_id=emp.id,
        status="ONLINE"
    )
    # Unassigned device
    dev2 = Device(
        company_id=company.id,
        device_uuid="WIN-DEV-UNASSIGNED",
        hostname="PC-SHARED-02",
        employee_id=None,
        status="REGISTERED"
    )
    db.session.add_all([dev1, dev2])
    db.session.commit()

    # Query all
    resp_all = client.get("/api/v1/devices", headers=auth_headers)
    assert resp_all.status_code == 200
    items = resp_all.get_json()["data"]["items"]
    assert len(items) >= 2

    # Query unassigned only
    resp_unassigned = client.get("/api/v1/devices?status=UNASSIGNED", headers=auth_headers)
    assert resp_unassigned.status_code == 200
    unassigned_items = resp_unassigned.get_json()["data"]["items"]
    assert all(d["employee_id"] is None for d in unassigned_items)
    assert any(d["device_uuid"] == "WIN-DEV-UNASSIGNED" for d in unassigned_items)

    # Search filter
    resp_search = client.get("/api/v1/devices?search=JANE", headers=auth_headers)
    assert resp_search.status_code == 200
    search_items = resp_search.get_json()["data"]["items"]
    assert any(d["device_uuid"] == "WIN-DEV-ASSIGNED" for d in search_items)

def test_device_assign_and_unassign_employee(client, auth_headers, db_session):
    """Test assigning and unassigning an employee from a device."""
    company = Company.query.first()
    emp = Employee(
        company_id=company.id,
        employee_code="EMP-200",
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@test.corp"
    )
    dev = Device(
        company_id=company.id,
        device_uuid="WIN-DEV-MGMT-001",
        hostname="PC-MGMT-01",
        status="REGISTERED"
    )
    db.session.add_all([emp, dev])
    db.session.commit()

    # Assign Employee
    assign_resp = client.post(
        f"/api/v1/devices/{dev.id}/assign",
        json={"employee_id": emp.id},
        headers=auth_headers
    )
    assert assign_resp.status_code == 200
    assert assign_resp.get_json()["data"]["employee_id"] == emp.id

    # Unassign Employee
    unassign_resp = client.post(
        f"/api/v1/devices/{dev.id}/unassign",
        headers=auth_headers
    )
    assert unassign_resp.status_code == 200
    assert unassign_resp.get_json()["data"]["employee_id"] is None

def test_device_disable_and_enable(client, auth_headers, db_session):
    """Test disabling and enabling a workstation device."""
    company = Company.query.first()
    dev = Device(
        company_id=company.id,
        device_uuid="WIN-DEV-TOGGLE",
        hostname="PC-TOGGLE",
        status="ONLINE"
    )
    db.session.add(dev)
    db.session.commit()

    # Disable
    dis_resp = client.post(f"/api/v1/devices/{dev.id}/disable", headers=auth_headers)
    assert dis_resp.status_code == 200
    assert dis_resp.get_json()["data"]["status"] == "DISABLED"

    # Enable
    en_resp = client.post(f"/api/v1/devices/{dev.id}/enable", headers=auth_headers)
    assert en_resp.status_code == 200
    assert en_resp.get_json()["data"]["status"] == "REGISTERED"

def test_device_details_endpoint(client, auth_headers, db_session):
    """Test GET /api/v1/devices/{id} returns comprehensive details without exposing secrets."""
    company = Company.query.first()
    now = datetime.now(timezone.utc)
    dev = Device(
        company_id=company.id,
        device_uuid="WIN-DEV-DETAIL-001",
        hostname="PC-DETAIL-001",
        operating_system="Windows 11 Pro",
        agent_version="1.0.0",
        status="ONLINE",
        last_seen_at=now
    )
    db.session.add(dev)
    db.session.commit()

    resp = client.get(f"/api/v1/devices/{dev.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["hostname"] == "PC-DETAIL-001"
    assert data["operating_system"] == "Windows 11 Pro"
    assert data["status"] == "ONLINE"
    assert "audit_history" in data
    assert "websocket_status" in data
    assert "registration_token_hash" not in data
