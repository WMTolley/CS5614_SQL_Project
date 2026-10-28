"""End-to-end tests of the account endpoints against a real database.
Skipped when the database is unreachable (it rebuilds the schema, like the backend does)."""

import importlib
import uuid

import pytest

PASSWORD = "a-good-password"
# Employee 3 (Jace One, WarehouseStaff) is active; employee 24 (Zoe Carter) has left
ACTIVE_EMPLOYEE_ID = 3
TERMINATED_EMPLOYEE_ID = 24


def new_username():
    return f"user_{uuid.uuid4().hex[:12]}"


def signup(client, username, password=PASSWORD, **overrides):
    body = {
        "name": "Test Customer",
        "email": "test@example.com",
        "username": username,
        "password": password,
    }
    body.update(overrides)
    return client.post("/auth/signup", json=body)


def login(client, username, password=PASSWORD):
    return client.post(
        "/auth/login", json={"username": username, "password": password}
    )


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def logged_in_token(client):
    username = new_username()
    assert signup(client, username).status_code == 201
    response = login(client, username)
    assert response.status_code == 200
    return response.json()["token"]


def test_signup_login_and_me(client):
    username = new_username()
    assert signup(client, username).status_code == 201

    response = login(client, username)
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "Customer"
    assert body["user"]["username"] == username

    me = client.get("/auth/me", headers=auth(body["token"]))
    assert me.status_code == 200
    assert me.json() == body["user"]


def test_responses_never_contain_the_password_or_hash(client):
    username = new_username()
    responses = [
        signup(client, username),
        login(client, username),
        client.get("/auth/me", headers=auth(login(client, username).json()["token"])),
    ]
    for response in responses:
        assert PASSWORD not in response.text
        assert "password" not in response.text.lower()
        assert "$2b$" not in response.text


def test_signup_username_is_unique_ignoring_case(client):
    username = new_username()
    assert signup(client, username).status_code == 201
    assert signup(client, username).status_code == 400
    assert signup(client, username.upper()).status_code == 400


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "short"},
        {"password": "x" * 73},
        {"email": None, "phone": None},
        {"username": "ab"},
    ],
)
def test_signup_rejects_bad_input(client, overrides):
    overrides = dict(overrides)
    username = overrides.pop("username", new_username())
    response = signup(client, username, **overrides)
    assert response.status_code in (400, 422)


def test_failed_signup_leaves_no_orphaned_customer(client):
    username = new_username()
    assert signup(client, username).status_code == 201
    # Same username, so the account insert fails after the customer insert succeeded
    assert signup(client, username, name="Orphan Check").status_code == 400

    backend = importlib.import_module("backend.backend")
    with backend.connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM customer WHERE name = 'Orphan Check';")
        assert cur.fetchone()[0] == 0


@pytest.mark.parametrize(
    "username, password",
    [
        ("no_such_user_anywhere", PASSWORD),
        ("__existing__", "wrong-password"),
    ],
)
def test_bad_login_gets_the_same_generic_error(client, username, password):
    existing = new_username()
    signup(client, existing)
    username = existing if username == "__existing__" else username

    response = login(client, username, password)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password."


def test_login_username_is_case_insensitive(client):
    username = new_username()
    signup(client, username)
    assert login(client, username.upper()).status_code == 200


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/auth/me"),
        ("post", "/auth/logout"),
        ("post", "/auth/change-password"),
        ("post", "/admin/users"),
    ],
)
def test_protected_endpoints_need_a_valid_token(client, method, path):
    assert getattr(client, method)(path).status_code == 401
    bad = getattr(client, method)(path, headers=auth("not-a-real-token"))
    assert bad.status_code == 401


def test_logout_invalidates_the_token(client):
    token = logged_in_token(client)
    assert client.get("/auth/me", headers=auth(token)).status_code == 200
    assert client.post("/auth/logout", headers=auth(token)).status_code == 200
    assert client.get("/auth/me", headers=auth(token)).status_code == 401


def test_change_password(client):
    username = new_username()
    signup(client, username)
    token = login(client, username).json()["token"]
    other_token = login(client, username).json()["token"]

    wrong = client.post(
        "/auth/change-password",
        headers=auth(token),
        json={"old_password": "not-my-password", "new_password": "brand-new-pass"},
    )
    assert wrong.status_code == 400

    too_short = client.post(
        "/auth/change-password",
        headers=auth(token),
        json={"old_password": PASSWORD, "new_password": "short"},
    )
    assert too_short.status_code == 400

    ok = client.post(
        "/auth/change-password",
        headers=auth(token),
        json={"old_password": PASSWORD, "new_password": "brand-new-pass"},
    )
    assert ok.status_code == 200

    assert login(client, username, PASSWORD).status_code == 401
    assert login(client, username, "brand-new-pass").status_code == 200
    # The session that changed it stays logged in; the other session is ended
    assert client.get("/auth/me", headers=auth(token)).status_code == 200
    assert client.get("/auth/me", headers=auth(other_token)).status_code == 401


def test_admin_can_log_in(client, admin_headers):
    response = client.get("/auth/me", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "Admin"
    assert response.json()["is_admin"] is True


def test_non_admin_cannot_create_users(client):
    token = logged_in_token(client)
    response = client.post(
        "/admin/users",
        headers=auth(token),
        json={"username": new_username(), "password": PASSWORD, "is_admin": True},
    )
    assert response.status_code == 403


def test_admin_creates_an_employee_account_with_the_employee_role(client, admin_headers):
    username = new_username()
    response = client.post(
        "/admin/users",
        headers=admin_headers,
        json={
            "username": username,
            "password": PASSWORD,
            "employee_id": ACTIVE_EMPLOYEE_ID,
        },
    )
    assert response.status_code == 201

    user = login(client, username).json()["user"]
    assert user["role"] == "WarehouseStaff"
    assert user["employee_id"] == ACTIVE_EMPLOYEE_ID

    # That employee already has an account now
    again = client.post(
        "/admin/users",
        headers=admin_headers,
        json={
            "username": new_username(),
            "password": PASSWORD,
            "employee_id": ACTIVE_EMPLOYEE_ID,
        },
    )
    assert again.status_code == 400


@pytest.mark.parametrize(
    "extra",
    [
        {"employee_id": TERMINATED_EMPLOYEE_ID},  # employee has left
        {"employee_id": 99999},  # no such employee
        {"customer_id": 1, "employee_id": 1},  # two profiles
        {},  # no profile and not an admin
        {"password": "short", "is_admin": True},
    ],
)
def test_admin_create_user_rejects_invalid_accounts(client, admin_headers, extra):
    body = {"username": new_username(), "password": PASSWORD}
    body.update(extra)
    response = client.post(
        "/admin/users", headers=admin_headers, json=body
    )
    assert response.status_code == 400


def test_sql_injection_text_is_treated_as_plain_data(client):
    username = "x'; DROP TABLE customer; --"
    assert signup(client, username).status_code == 201
    response = login(client, username)
    assert response.status_code == 200

    # A classic injection in the login form must not log anyone in
    assert login(client, "' OR '1'='1", "' OR '1'='1").status_code == 401

    # The customer table is still there, and the username was stored as plain text
    backend = importlib.import_module("backend.backend")
    with backend.connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM userAccount WHERE username = %s;", (username,))
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM customer;")
        assert cur.fetchone()[0] > 0
