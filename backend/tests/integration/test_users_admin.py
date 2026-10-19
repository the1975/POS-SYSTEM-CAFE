import pytest
from sqlalchemy import select

from app.modules.audit.model import AuditLog
from app.modules.users.admin_service import UserAdminService
from app.modules.users.exceptions import LastAdminError
from app.modules.users.model import Role, User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserUpdateIn

API = "/api/v1"
ROLE_NAMES = ["ADMIN", "CONTROLLER", "KITCHEN", "CASHIER", "PICKUP"]
PASSWORD_BARU = "password-baru-12345"


def _roles(db):
    ids = {}
    for name in ROLE_NAMES:
        role = db.scalar(select(Role).where(Role.name == name))
        if role is None:
            role = Role(name=name)
            db.add(role)
            db.flush()
        ids[name] = role.id
    db.commit()
    return ids


def _user_id(db, email):
    return db.scalar(select(User.id).where(User.email == email))


def _new_user_body(roles, **override):
    body = {
        "name": "Dapur Satu",
        "email": "Dapur1@Example.com",
        "password": PASSWORD_BARU,
        "role_id": str(roles["KITCHEN"]),
    }
    body.update(override)
    return body


def test_admin_lists_users_without_password_fields(client, db, staff_headers):
    _roles(db)
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/users", headers=admin)
    assert r.status_code == 200
    item = r.json()["data"][0]
    assert set(item) == {"id", "name", "email", "role", "role_id", "is_active", "created_at"}
    assert item["role"] == "ADMIN"
    assert "password" not in r.text
    assert r.json()["pagination"]["total"] == 1


def test_only_admin_can_manage_users(client, db, staff_headers):
    roles = _roles(db)
    cashier = staff_headers("CASHIER")
    target = str(roles["CASHIER"])
    assert client.get(f"{API}/users", headers=cashier).status_code == 403
    assert client.get(f"{API}/users/roles", headers=cashier).status_code == 403
    r = client.post(f"{API}/users", json=_new_user_body(roles), headers=cashier)
    assert r.status_code == 403
    r = client.patch(f"{API}/users/{target}", json={"name": "X"}, headers=cashier)
    assert r.status_code == 403
    assert client.get(f"{API}/users").status_code == 401


def test_roles_endpoint_lists_all_roles(client, db, staff_headers):
    _roles(db)
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/users/roles", headers=admin)
    assert r.status_code == 200
    assert [x["name"] for x in r.json()["data"]] == sorted(ROLE_NAMES)


def test_admin_creates_user_who_can_login(client, db, staff_headers):
    roles = _roles(db)
    admin = staff_headers("ADMIN")
    r = client.post(f"{API}/users", json=_new_user_body(roles), headers=admin)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert (data["role"], data["is_active"], data["email"]) == (
        "KITCHEN",
        True,
        "dapur1@example.com",
    )

    login = client.post(
        f"{API}/auth/login", json={"email": "dapur1@example.com", "password": PASSWORD_BARU}
    )
    assert login.status_code == 200
    assert login.json()["data"]["user"]["role"] == "KITCHEN"

    audit = db.scalars(select(AuditLog).where(AuditLog.action == "CREATE_USER")).one()
    assert audit.new_value == {
        "name": "Dapur Satu",
        "email": "dapur1@example.com",
        "role": "KITCHEN",
    }
    assert PASSWORD_BARU not in str(audit.new_value)


def test_duplicate_email_and_unknown_role_rejected(client, db, staff_headers):
    roles = _roles(db)
    admin = staff_headers("ADMIN")
    assert client.post(f"{API}/users", json=_new_user_body(roles), headers=admin).status_code == 201
    dup = _new_user_body(roles, email="DAPUR1@example.COM")
    r = client.post(f"{API}/users", json=dup, headers=admin)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EMAIL_ALREADY_USED"

    unknown = _new_user_body(
        roles, email="lain@example.com", role_id="11111111-1111-1111-1111-111111111111"
    )
    r = client.post(f"{API}/users", json=unknown, headers=admin)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "ROLE_NOT_FOUND"


@pytest.mark.parametrize(
    "override",
    [{"password": "pendek"}, {"email": "bukan-email"}, {"name": "   "}, {"role_id": "bukan-uuid"}],
)
def test_create_user_validation(client, db, staff_headers, override):
    roles = _roles(db)
    admin = staff_headers("ADMIN")
    r = client.post(f"{API}/users", json=_new_user_body(roles, **override), headers=admin)
    assert r.status_code == 422


def test_admin_updates_name_and_role_with_audit(client, db, staff_headers):
    roles = _roles(db)
    admin = staff_headers("ADMIN")
    staff_headers("CASHIER")
    uid = _user_id(db, "cashier@example.com")

    r = client.patch(
        f"{API}/users/{uid}",
        json={"name": "Kasir Baru", "role_id": str(roles["PICKUP"])},
        headers=admin,
    )
    assert r.status_code == 200, r.text
    assert (r.json()["data"]["name"], r.json()["data"]["role"]) == ("Kasir Baru", "PICKUP")

    audit = db.scalars(select(AuditLog).where(AuditLog.action == "UPDATE_USER")).one()
    assert audit.old_value == {"name": "Staf CASHIER", "role": "CASHIER", "is_active": True}
    assert audit.new_value == {"name": "Kasir Baru", "role": "PICKUP", "is_active": True}


def test_deactivated_user_loses_access_immediately(client, db, staff_headers):
    _roles(db)
    admin = staff_headers("ADMIN")
    kitchen = staff_headers("KITCHEN")
    uid = _user_id(db, "kitchen@example.com")
    assert client.get(f"{API}/auth/me", headers=kitchen).status_code == 200

    r = client.patch(f"{API}/users/{uid}", json={"is_active": False}, headers=admin)
    assert r.status_code == 200
    assert r.json()["data"]["is_active"] is False
    assert client.get(f"{API}/auth/me", headers=kitchen).status_code == 401
    login = client.post(
        f"{API}/auth/login", json={"email": "kitchen@example.com", "password": "password-uji-12345"}
    )
    assert login.status_code == 401

    r = client.patch(f"{API}/users/{uid}", json={"is_active": True}, headers=admin)
    assert r.status_code == 200
    assert client.get(f"{API}/auth/me", headers=kitchen).status_code == 200


def test_admin_cannot_lock_themselves_out(client, db, staff_headers):
    roles = _roles(db)
    admin = staff_headers("ADMIN")
    me = _user_id(db, "admin@example.com")

    r = client.patch(f"{API}/users/{me}", json={"is_active": False}, headers=admin)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CANNOT_MODIFY_SELF"
    r = client.patch(f"{API}/users/{me}", json={"role_id": str(roles["CASHIER"])}, headers=admin)
    assert r.status_code == 409
    # Mengganti nama sendiri tetap boleh.
    r = client.patch(f"{API}/users/{me}", json={"name": "Admin Utama"}, headers=admin)
    assert r.status_code == 200
    assert client.get(f"{API}/auth/me", headers=admin).status_code == 200


def test_update_requires_a_field_and_existing_user(client, db, staff_headers):
    _roles(db)
    admin = staff_headers("ADMIN")
    uid = _user_id(db, "admin@example.com")
    assert client.patch(f"{API}/users/{uid}", json={}, headers=admin).status_code == 422
    missing = "22222222-2222-2222-2222-222222222222"
    r = client.patch(f"{API}/users/{missing}", json={"name": "X"}, headers=admin)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "USER_NOT_FOUND"


def test_last_active_admin_cannot_be_removed(client, db, staff_headers):
    roles = _roles(db)
    staff_headers("ADMIN")
    admin_id = _user_id(db, "admin@example.com")
    other = User(
        role_id=roles["CASHIER"], name="Kasir", email="kasir@example.com", password_hash="x"
    )
    db.add(other)
    db.commit()

    # Dipanggil langsung lewat service dengan "pelaku" non-admin untuk menguji pengaman ini.
    service = UserAdminService(UserRepository(db))
    with pytest.raises(LastAdminError):
        service.update(admin_id, UserUpdateIn(is_active=False), other)
    with pytest.raises(LastAdminError):
        service.update(admin_id, UserUpdateIn(role_id=roles["CASHIER"]), other)
    assert db.scalar(select(User.is_active).where(User.id == admin_id)) is True


def test_list_filters_by_role_status_and_search(client, db, staff_headers):
    roles = _roles(db)
    admin = staff_headers("ADMIN")
    staff_headers("CASHIER")
    staff_headers("KITCHEN")
    uid = _user_id(db, "kitchen@example.com")
    client.patch(f"{API}/users/{uid}", json={"is_active": False}, headers=admin)

    def names(**params):
        r = client.get(f"{API}/users", params=params, headers=admin)
        assert r.status_code == 200
        return sorted(u["email"] for u in r.json()["data"])

    assert len(names()) == 3
    assert names(role_id=str(roles["CASHIER"])) == ["cashier@example.com"]
    assert names(is_active="false") == ["kitchen@example.com"]
    assert names(is_active="true") == ["admin@example.com", "cashier@example.com"]
    assert names(search="kitchen") == ["kitchen@example.com"]
    assert names(search="STAF CASH") == ["cashier@example.com"]
