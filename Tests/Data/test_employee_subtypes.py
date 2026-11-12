"""Checks the employee supertype/subtype tables agree with each other in both seed files.
Needs the real database; skipped when it is unreachable."""

import psycopg2
import pytest

from db.sql_commands import connect_and_init

SEED_FILES = ["db/Data/seed.sql", "db/Data/inventory_testing.sql"]

# employee_type -> its subtype table
SUBTYPE_TABLES = {
    "WarehouseStaff": "warehouseStaff",
    "Supervisor": "supervisor",
    "InventoryManager": "inventoryManager",
}


@pytest.fixture(scope="module", params=SEED_FILES)
def conn(request):
    try:
        connection = connect_and_init("db/Data/schema.sql", request.param)
    except RuntimeError:
        pytest.skip("Database container not reachable.")
    yield connection
    connection.close()


def rows(conn, query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def test_seed_has_employees_of_every_type(conn):
    types = {t for (t,) in rows(conn, "SELECT DISTINCT employee_type FROM employee;")}
    assert types >= {"WarehouseStaff", "Supervisor"}


@pytest.mark.parametrize("employee_type, table", SUBTYPE_TABLES.items())
def test_every_employee_has_a_matching_subtype_row(conn, employee_type, table):
    missing = rows(
        conn,
        f"""
        SELECT e.employee_id, e.name
        FROM employee e
        LEFT JOIN {table} s ON s.employee_id = e.employee_id
        WHERE e.employee_type = '{employee_type}' AND s.employee_id IS NULL;
        """,
    )
    assert missing == [], f"{employee_type} employees with no {table} row: {missing}"


@pytest.mark.parametrize("employee_type, table", SUBTYPE_TABLES.items())
def test_every_subtype_row_belongs_to_an_employee_of_that_type(conn, employee_type, table):
    wrong = rows(
        conn,
        f"""
        SELECT s.employee_id
        FROM {table} s
        JOIN employee e ON e.employee_id = s.employee_id
        WHERE e.employee_type <> '{employee_type}';
        """,
    )
    assert wrong == []


def test_no_employee_is_in_two_subtype_tables(conn):
    duplicated = rows(
        conn,
        """
        SELECT employee_id FROM (
            SELECT employee_id FROM warehouseStaff
            UNION ALL SELECT employee_id FROM supervisor
            UNION ALL SELECT employee_id FROM inventoryManager
        ) all_subtypes
        GROUP BY employee_id HAVING count(*) > 1;
        """,
    )
    assert duplicated == []


# The database itself must refuse a subtype row for the wrong kind of employee
@pytest.mark.parametrize(
    "insert",
    [
        # employee 1 is a Supervisor in both seeds
        "INSERT INTO warehouseStaff (employee_id, role_type) VALUES (1, 'Picker')",
        "INSERT INTO inventoryManager (employee_id) VALUES (1)",
        # a subtype row can't claim to be another type
        "INSERT INTO supervisor (employee_id, employee_type) VALUES (1, 'WarehouseStaff')",
        # no such employee
        "INSERT INTO supervisor (employee_id) VALUES (99999)",
    ],
)
def test_database_rejects_mismatched_subtype_rows(conn, insert):
    with pytest.raises(psycopg2.Error):
        with conn.cursor() as cur:
            cur.execute(insert)
    conn.rollback()


def test_database_blocks_changing_the_type_of_an_employee_with_a_subtype_row(conn):
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE employee SET employee_type = 'WarehouseStaff' WHERE employee_id = 1;"
            )
    conn.rollback()
