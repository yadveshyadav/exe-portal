import pytest
from app import create_app
from app.extensions import db
from app.models.company import Company
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.employee import Employee
from app.models.device import Device
from app.modules.auth.permissions import DEFAULT_PERMISSIONS

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        # Clean state
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        # Seed basic permissions & company
        perm_map = {}
        for code, name, module in DEFAULT_PERMISSIONS:
            perm = Permission(code=code, name=name, module=module)
            db.session.add(perm)
            perm_map[code] = perm

        company = Company(code="TEST_CORP", name="Test Corporation")
        db.session.add(company)
        db.session.flush()

        role = Role(company_id=company.id, name="SuperAdmin", code="SUPER_ADMIN", is_system=True)
        role.permissions = list(perm_map.values())
        db.session.add(role)
        db.session.flush()

        admin = User(
            company_id=company.id,
            username="testadmin",
            email="admin@test.corp",
            is_superuser=True,
            status="ACTIVE"
        )
        admin.set_password("Admin@123456")
        admin.roles = [role]
        db.session.add(admin)
        db.session.commit()

        yield db.session

@pytest.fixture
def auth_headers(client, db_session):
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "testadmin",
        "password": "Admin@123456"
    })
    token = resp.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
