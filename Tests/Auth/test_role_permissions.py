"""Tests that each inventory endpoint is limited to the right roles, and that the writes
behave. Needs the real database (see conftest.py)."""

import importlib
import uuid

import pytest

PASSWORD = "a-good-password"
# One seeded employee of each type; none of them is used by test_auth_endpoints.py
EMPLOYEES = {"WarehouseStaff": 14, "Supervisor": 5, "InventoryManager": 9}
# Role ranks, lowest first; Admin is not on the ladder
LADDER = ["Customer", "WarehouseStaff", "Supervisor", "InventoryManager"]
ROLES = LADDER + ["Admin"]


def unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def log_in(client, username):
    response = client.post(
        "/auth/login", json={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def headers(client, admin_headers):
    """A logged-in Authorization header for one account of every role"""
    result = {"Admin": admin_headers}

    username = unique("customer")
    response = client.post(
        "/auth/signup",
        json={
            "name": "Role Test",
            "email": "role@example.com",
            "username": username,
            "password": PASSWORD,
        },
    )
    assert response.status_code == 201
    result["Customer"] = bearer(log_in(client, username)["token"])

    for role, employee_id in EMPLOYEES.items():
        username = unique(role.lower())
        response = client.post(
            "/admin/users",
            headers=admin_headers,
            json={
                "username": username,
                "password": PASSWORD,
                "employee_id": employee_id,
            },
        )
        assert response.status_code == 201
        session = log_in(client, username)
        assert session["user"]["role"] == role
        result[role] = bearer(session["token"])
    return result


# (method, path, body factory, lowest role allowed). The factories give each call fresh data.
ENDPOINTS = [
    ("GET", "/read", lambda: None, "Customer"),
    ("GET", "/search?name=nowhere", lambda: None, "Customer"),
    (
        "POST",
        "/insert",
        lambda: {"name": "Widget", "serial_number": unique("SN")},
        "Supervisor",
    ),
    (
        "PUT",
        "/update/99999",
        lambda: {"new_price": 2.5},
        "Supervisor",
    ),
    (
        "POST",
        "/insert_warehouse",
        lambda: {"name": unique("Warehouse")},
        "InventoryManager",
    ),
    (
        "PUT",
        "/update_warehouse/99999",
        lambda: {"is_public": True},
        "InventoryManager",
    ),
    ("DELETE", "/delete/99999", lambda: None, "InventoryManager"),
]


@pytest.mark.parametrize(
    "method, path, make_body, min_role", ENDPOINTS, ids=[e[1] for e in ENDPOINTS]
)
@pytest.mark.parametrize("role", ROLES)
def test_role_access_matrix(client, headers, role, method, path, make_body, min_role):
    response = client.request(method, path, headers=headers[role], json=make_body())

    allowed = role in LADDER and LADDER.index(role) >= LADDER.index(min_role)
    if allowed:
        # Anything but a rejection; the call itself may still 404/409 on made-up ids
        assert response.status_code not in (401, 403)
    else:
        assert response.status_code == 403


@pytest.mark.parametrize(
    "method, path, make_body, min_role", ENDPOINTS, ids=[e[1] for e in ENDPOINTS]
)
def test_inventory_endpoints_need_login(client, method, path, make_body, min_role):
    assert client.request(method, path, json=make_body()).status_code == 401
    bad = client.request(method, path, headers=bearer("nope"), json=make_body())
    assert bad.status_code == 401


def test_health_check_stays_open(client):
    assert client.get("/").status_code == 200


@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/insert/Widget/SN1"),
        ("GET", "/insert_warehouse/Name"),
        ("GET", "/update/2/5.50"),
        ("GET", "/update_warehouse/7/true"),
        ("GET", "/delete/7"),
    ],
)
def test_old_get_mutation_urls_are_gone(client, headers, method, path):
    response = client.request(method, path, headers=headers["InventoryManager"])
    assert response.status_code in (404, 405)


def new_item(client, headers, **overrides):
    body = {"name": "Widget", "serial_number": unique("SN")}
    body.update(overrides)
    return client.post("/insert", headers=headers["Supervisor"], json=body)


def test_insert_records_the_logged_in_employee(client, headers):
    response = new_item(client, headers)
    assert response.status_code == 201
    item_id = response.json()["item_id"]

    backend = importlib.import_module("backend.backend")
    with backend.connection.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT employee_id FROM statusChange WHERE item_id = %s;",
            (item_id,),
        )
        assert cur.fetchall() == [(EMPLOYEES["Supervisor"],)]
        cur.execute("SELECT status FROM item WHERE item_id = %s;", (item_id,))
        assert cur.fetchone() == ("In Stock",)


def test_manager_can_also_insert_items_by_inheritance(client, headers):
    response = client.post(
        "/insert",
        headers=headers["InventoryManager"],
        json={"name": "Widget", "serial_number": unique("SN")},
    )
    assert response.status_code == 201


@pytest.mark.parametrize(
    "overrides",
    [
        {"category_id": 99999},
        {"warehouse_id": 99999},
    ],
)
def test_insert_with_unknown_references_fails_cleanly(client, headers, overrides):
    assert new_item(client, headers, **overrides).status_code == 400


def test_insert_duplicate_serial_fails_cleanly(client, headers):
    serial = unique("SN")
    assert new_item(client, headers, serial_number=serial).status_code == 201
    assert new_item(client, headers, serial_number=serial).status_code == 400


@pytest.mark.parametrize("body", [{"name": ""}, {"serial_number": ""}, {"markup_price": -1}])
def test_insert_validates_input(client, headers, body):
    assert new_item(client, headers, **body).status_code == 422


def test_update_price(client, headers):
    item_id = new_item(client, headers).json()["item_id"]
    response = client.put(
        f"/update/{item_id}", headers=headers["Supervisor"], json={"new_price": 7.25}
    )
    assert response.status_code == 200

    backend = importlib.import_module("backend.backend")
    with backend.connection.cursor() as cur:
        cur.execute("SELECT markup_price FROM item WHERE item_id = %s;", (item_id,))
        assert float(cur.fetchone()[0]) == 7.25


@pytest.mark.parametrize("body", [{"new_price": -1}, {}])
def test_update_price_validates_input(client, headers, body):
    response = client.put("/update/1", headers=headers["Supervisor"], json=body)
    assert response.status_code == 422


def test_update_price_of_missing_item_is_404(client, headers):
    response = client.put(
        "/update/99999", headers=headers["Supervisor"], json={"new_price": 1}
    )
    assert response.status_code == 404


def test_manager_warehouse_lifecycle(client, headers):
    manager = headers["InventoryManager"]
    name = unique("Lifecycle")

    created = client.post("/insert_warehouse", headers=manager, json={"name": name})
    assert created.status_code == 201
    warehouse_id = created.json()["warehouse_id"]

    # New warehouses default to public, so customers can see them
    listed = client.get("/read", headers=headers["Customer"]).json()["public warehouses"]
    assert warehouse_id in [row[0] for row in listed]

    private = client.put(
        f"/update_warehouse/{warehouse_id}", headers=manager, json={"is_public": False}
    )
    assert private.status_code == 200
    listed = client.get("/read", headers=headers["Customer"]).json()["public warehouses"]
    assert warehouse_id not in [row[0] for row in listed]

    assert client.delete(f"/delete/{warehouse_id}", headers=manager).status_code == 200
    assert client.delete(f"/delete/{warehouse_id}", headers=manager).status_code == 409


def test_cannot_delete_a_warehouse_that_has_items(client, headers):
    manager = headers["InventoryManager"]
    warehouse_id = client.post(
        "/insert_warehouse", headers=manager, json={"name": unique("Stocked")}
    ).json()["warehouse_id"]
    assert new_item(client, headers, warehouse_id=warehouse_id).status_code == 201

    assert client.delete(f"/delete/{warehouse_id}", headers=manager).status_code == 409


def test_duplicate_warehouse_name_fails_cleanly(client, headers):
    manager = headers["InventoryManager"]
    name = unique("Dup")
    assert client.post("/insert_warehouse", headers=manager, json={"name": name}).status_code == 201
    assert client.post("/insert_warehouse", headers=manager, json={"name": name}).status_code == 400


def test_update_missing_warehouse_is_404(client, headers):
    response = client.put(
        "/update_warehouse/99999",
        headers=headers["InventoryManager"],
        json={"is_public": True},
    )
    assert response.status_code == 404
