"""Prints the sample data, sample queries and constraint demonstrations for the project report.
Demo accounts and sessions are added in a transaction that is rolled back at the end.

Run with:  python -m db.sample_report            (uses the data already in the database)
           python -m db.sample_report --init     (reloads schema.sql and seed.sql first)
"""

import sys

import psycopg2

from db.auth import hash_password, hash_token, new_session_token
from db.sql_commands import DB_CONFIG, connect_and_init

SAMPLE_ROWS = 5

# (table, ORDER BY) for each table, grouped like Section 4.3
TABLES = [
    ("zipCode", "zip"),
    ("itemCategory", "category_id"),
    ("supplier", "supplier_id"),
    ("customer", "customer_id"),
    ("warehouse", "warehouse_id"),
    ("item", "item_id"),
    ("customerTransaction", "transaction_id"),
    ("itemReturn", "return_id"),
    ("supply", "supply_id"),
    ("statusChange", "status_change_id"),
    ("warehouseTransfer", "transfer_id"),
    ("employee", "employee_id"),
    ("warehouseStaff", "employee_id"),
    ("supervisor", "employee_id"),
    ("inventoryManager", "employee_id"),
    ("management", "employee_id, warehouse_id"),
    ("userAccount", "user_id"),
    ("userSession", "created_at"),
]

# Columns that hold secrets: only the start is shown
HIDDEN_COLUMNS = ("password_hash", "token_hash")

DEMO_PASSWORD = "DemoPass123"

# (username, role) of the demo accounts the report adds (rolled back at the end)
DEMO_ACCOUNTS = [
    ("demo.admin", "Admin"),
    ("demo.supervisor", "Supervisor"),
    ("demo.manager", "InventoryManager"),
    ("demo.staff", "WarehouseStaff"),
    ("demo.customer", "Customer"),
]

# Picks a profile that has no account yet, so a demo account never collides with a real one
FREE_CUSTOMER = """
    SELECT customer_id FROM customer
    WHERE customer_id NOT IN (SELECT customer_id FROM userAccount WHERE customer_id IS NOT NULL)
    ORDER BY customer_id LIMIT 1
"""
FREE_EMPLOYEE = """
    SELECT employee_id FROM employee
    WHERE employee_type = %s AND final_date IS NULL
      AND employee_id NOT IN (SELECT employee_id FROM userAccount WHERE employee_id IS NOT NULL)
    ORDER BY employee_id LIMIT 1
"""

# (title, what it shows, SQL)
QUERIES = [
    (
        "Public warehouses (Customer)",
        "Private warehouses are filtered out by is_public.",
        """
        SELECT name, street, zip
        FROM warehouse
        WHERE is_public
        ORDER BY name
        """,
    ),
    (
        "Available items in a warehouse (Customer)",
        "Only In Stock items in a public warehouse, grouped with a count and price.",
        """
        SELECT i.name, count(*) AS available, min(i.markup_price) AS price
        FROM item i
        JOIN warehouse w USING (warehouse_id)
        WHERE w.name = 'Washington DC Branch'
          AND w.is_public
          AND i.status = 'In Stock'
        GROUP BY i.name
        ORDER BY i.name
        """,
    ),
    (
        "Item count by warehouse and status (Supervisor)",
        "An aggregate over the six item statuses per warehouse (first 12 rows).",
        """
        SELECT w.name, i.status, count(*)
        FROM item i
        JOIN warehouse w USING (warehouse_id)
        GROUP BY w.name, i.status
        ORDER BY w.name, i.status
        LIMIT 12
        """,
    ),
    (
        "Supplier cost against markup price (Supervisor)",
        "A three-table join that computes the margin of each In Stock Office Lamp.",
        """
        SELECT i.serial_number, s.name AS supplier, sp.purchase_cost,
               i.markup_price, i.markup_price - sp.purchase_cost AS margin
        FROM item i
        JOIN supply sp USING (item_id)
        JOIN supplier s USING (supplier_id)
        WHERE i.name = 'Office Lamp' AND i.status = 'In Stock'
        ORDER BY i.serial_number
        """,
    ),
    (
        "Employees and their supervisors (Supervisor)",
        "A self-join on employee; the LEFT JOIN keeps the top supervisor, who has none.",
        """
        SELECT e.name AS employee, e.employee_type, s.name AS supervisor
        FROM employee e
        LEFT JOIN employee s ON s.employee_id = e.supervisor_id
        WHERE e.home_warehouse_id = 1
        ORDER BY e.employee_id
        """,
    ),
    (
        "Status-change audit trail for one employee (Supervisor)",
        "Every change is linked to the employee who made it.",
        """
        SELECT e.name, sc.old_status, sc.new_status, i.name AS item, sc.changed_at
        FROM statusChange sc
        JOIN employee e USING (employee_id)
        JOIN item i USING (item_id)
        WHERE e.employee_id = 17
        ORDER BY sc.changed_at
        """,
    ),
    (
        "Sales that were returned",
        "Follows customer, customerTransaction, item and itemReturn.",
        """
        SELECT c.name, ct.transaction_type, i.name AS item, r.return_condition
        FROM customerTransaction ct
        JOIN customer c USING (customer_id)
        JOIN item i USING (item_id)
        JOIN itemReturn r USING (transaction_id)
        ORDER BY ct.transaction_id
        """,
    ),
    (
        "Warehouse transfers",
        "Joins warehouse twice, as origin and as destination.",
        """
        SELECT t.transfer_date::date AS transfer_date, i.name,
               o.name AS origin, d.name AS destination
        FROM warehouseTransfer t
        JOIN item i USING (item_id)
        JOIN warehouse o ON o.warehouse_id = t.origin_warehouse_id
        JOIN warehouse d ON d.warehouse_id = t.destination_warehouse_id
        ORDER BY t.transfer_date
        """,
    ),
    (
        "Managers and the warehouses they run (Inventory Manager)",
        "The management junction table (many-to-many) with string_agg.",
        """
        SELECT e.name AS manager,
               string_agg(w.name, ', ' ORDER BY w.name) AS warehouses
        FROM management m
        JOIN employee e USING (employee_id)
        JOIN warehouse w USING (warehouse_id)
        GROUP BY e.name
        ORDER BY e.name
        """,
    ),
    (
        "Items sold per category",
        "Counts Sale transactions per category, ignoring Reservations.",
        """
        SELECT c.name, count(*) AS sold
        FROM customerTransaction ct
        JOIN item i USING (item_id)
        JOIN itemCategory c USING (category_id)
        WHERE ct.transaction_type = 'Sale'
        GROUP BY c.name
        ORDER BY sold DESC, c.name
        """,
    ),
    (
        "User accounts and their roles (Admin)",
        "The role is derived from is_admin, customer_id and employee_id.",
        """
        SELECT u.user_id, u.username,
               CASE WHEN u.is_admin THEN 'Admin'
                    WHEN u.customer_id IS NOT NULL THEN 'Customer'
                    ELSE e.employee_type END AS role,
               left(u.password_hash, 7) || '...' AS hash
        FROM userAccount u
        LEFT JOIN employee e USING (employee_id)
        ORDER BY u.user_id
        """,
    ),
    (
        "Active login sessions",
        "Sessions store only a hash of the token and last 24 hours.",
        """
        SELECT left(token_hash, 10) || '...' AS token_hash, u.username,
               s.expires_at - s.created_at AS lifetime
        FROM userSession s
        JOIN userAccount u USING (user_id)
        ORDER BY u.user_id
        """,
    ),
]

# (title, SQL) - each breaks a rule and must be rejected by the database
CONSTRAINT_DEMOS = [
    (
        "Negative price",
        """
        INSERT INTO item (name, serial_number, status, markup_price, category_id, warehouse_id)
        VALUES ('X', 'BAD-1', 'In Stock', -1, 1, 1)
        """,
    ),
    (
        "Duplicate serial number",
        """
        INSERT INTO item (name, serial_number, status, markup_price, category_id, warehouse_id)
        VALUES ('X', 'DC-ELEC-99281', 'In Stock', 1, 1, 1)
        """,
    ),
    ("Invalid item status", "UPDATE item SET status = 'Lost' WHERE item_id = 1"),
    (
        "Transfer to the same warehouse",
        """
        INSERT INTO warehouseTransfer (transfer_date, item_id, origin_warehouse_id, destination_warehouse_id)
        VALUES (now(), 1, 1, 1)
        """,
    ),
    ("Delete a warehouse that still has items", "DELETE FROM warehouse WHERE warehouse_id = 1"),
    (
        "Customer with no email or phone",
        "INSERT INTO customer (name, email, phone) VALUES ('No Contact', NULL, NULL)",
    ),
    (
        "Admin linked to a customer",
        """
        INSERT INTO userAccount (username, password_hash, is_admin, customer_id)
        VALUES ('bad', 'x', true, 2)
        """,
    ),
    (
        "Username differing only in case",
        """
        INSERT INTO userAccount (username, password_hash, customer_id)
        VALUES ('DEMO.ADMIN', 'x', 2)
        """,
    ),
]


def format_table(columns, rows):
    """Lays the rows out as an aligned text table"""
    text = [["NULL" if value is None else str(value) for value in row] for row in rows]
    widths = [
        max([len(column)] + [len(row[i]) for row in text])
        for i, column in enumerate(columns)
    ]
    lines = [
        " | ".join(column.ljust(width) for column, width in zip(columns, widths)),
        "-+-".join("-" * width for width in widths),
    ]
    for row in text:
        lines.append(" | ".join(cell.ljust(width) for cell, width in zip(row, widths)))
    return "\n".join(lines)


def run_query(conn, query):
    """Runs a read-only query and returns it as a text table"""
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column.name for column in cur.description]
        return format_table(columns, cur.fetchall())


def heading(text, char="="):
    """Prints a heading with an underline"""
    print(f"\n{text}\n{char * len(text)}")


def add_demo_accounts(conn):
    """Adds one account and one session per role so userAccount and userSession have rows.
    Nothing is committed: main() rolls the whole transaction back"""
    with conn.cursor() as cur:
        for username, role in DEMO_ACCOUNTS:
            if role == "Admin":
                profile = "NULL, NULL"
                params = []
            elif role == "Customer":
                profile = f"({FREE_CUSTOMER}), NULL"
                params = []
            else:
                profile = f"NULL, ({FREE_EMPLOYEE})"
                params = [role]
            cur.execute(
                f"""
                INSERT INTO userAccount (username, password_hash, is_admin, customer_id, employee_id)
                VALUES (%s, %s, %s, {profile})
                RETURNING user_id
                """,
                [username, hash_password(DEMO_PASSWORD), role == "Admin"] + params,
            )
            cur.execute(
                """
                INSERT INTO userSession (token_hash, user_id, expires_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '24 hours')
                """,
                (hash_token(new_session_token()), cur.fetchone()[0]),
            )
    print(
        f"Added {len(DEMO_ACCOUNTS)} demo accounts and sessions for this report only "
        "(rolled back when it finishes; the database is not changed)."
    )


def show_sample_data(conn):
    """Prints the row count and the first rows of every table"""
    heading("4.4.1 Sample Data")
    for number, (table, order_by) in enumerate(TABLES, 1):
        with conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM {table}")
            total = cur.fetchone()[0]
        heading(f"Table {number}: {table} ({total} rows, first {SAMPLE_ROWS} shown)", "-")
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table} ORDER BY {order_by} LIMIT {SAMPLE_ROWS}")
            columns = [column.name for column in cur.description]
            rows = [
                [
                    str(value)[:10] + "..." if column in HIDDEN_COLUMNS else value
                    for column, value in zip(columns, row)
                ]
                for row in cur.fetchall()
            ]
        print(format_table(columns, rows))


def show_queries(conn):
    """Prints each sample query with its result"""
    heading("4.4.2 Sample Queries")
    for number, (title, purpose, query) in enumerate(QUERIES, 1):
        heading(f"Query {number}: {title}", "-")
        print(f"{purpose}\n")
        print("\n".join(line[8:] for line in query.strip("\n").splitlines()))
        print(f"\n{run_query(conn, query)}")


def show_constraint_demos(conn):
    """Runs statements that break a rule and prints the database's rejection.
    Each is undone, so nothing is ever changed"""
    heading("4.4.3 Constraint Demonstrations")
    for number, (title, statement) in enumerate(CONSTRAINT_DEMOS, 1):
        heading(f"Demo {number}: {title}", "-")
        print("\n".join(line[8:] for line in statement.strip("\n").splitlines()))
        with conn.cursor() as cur:
            # A savepoint undoes just this statement and keeps the demo accounts
            cur.execute("SAVEPOINT demo")
            try:
                cur.execute(statement)
                print("\nUNEXPECTED: the database accepted this statement.")
            except psycopg2.Error as e:
                print(f"\nRejected: {e.pgerror.splitlines()[0].removeprefix('ERROR:  ')}")
            finally:
                cur.execute("ROLLBACK TO SAVEPOINT demo")


def main():
    """Prints the whole report to the terminal"""
    if "--init" in sys.argv:
        conn = connect_and_init("db/Data/schema.sql", "db/Data/seed.sql")
    else:
        conn = psycopg2.connect(**DB_CONFIG)
    try:
        add_demo_accounts(conn)
        show_sample_data(conn)
        show_queries(conn)
        show_constraint_demos(conn)
    finally:
        conn.rollback()
        conn.close()


if __name__ == "__main__":
    main()
