"""Handles the SQL Read Commands for Account Commands"""

import psycopg2
from psycopg2.extras import RealDictCursor


def read_customer_account_signin(
    conn, hashed_password, name=None, email=None, phone=None
) -> int:

    if not any([name, email, phone]):
        return -1

    query_warehouse = """
        SELECT c.customer_id 
        FROM customer c 
        WHERE (%s::varchar IS NULL OR c.name = %s) 
          AND (%s::varchar IS NULL OR c.email = %s) 
          AND (%s::varchar IS NULL OR c.phone = %s) 
          AND c.hashed_password = %s
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(
                query_warehouse,
                (name, name, email, email, phone, phone, hashed_password),
            )
            warehouse_row = cur.fetchall()

            if not warehouse_row:
                return -1

            if len(warehouse_row) > 1:
                return -1

            warehouse_id = warehouse_row[0]["customer_id"]
            return warehouse_id

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return -1


def read_employee_account_signin(
    conn, hashed_password, name=None, email=None, phone=None
) -> int:

    if not any([name, email, phone]):
        return -1

    query_warehouse = """
        SELECT e.employee_id 
        FROM employee e 
        WHERE (%s::varchar IS NULL OR e.name = %s) 
          AND (%s::varchar IS NULL OR e.email = %s) 
          AND (%s::varchar IS NULL OR e.phone = %s) 
          AND e.hashed_password = %s
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(
                query_warehouse,
                (name, name, email, email, phone, phone, hashed_password),
            )
            warehouse_row = cur.fetchall()

            if not warehouse_row:
                return -1

            if len(warehouse_row) > 1:
                return -1

            warehouse_id = warehouse_row[0]["employee_id"]
            return warehouse_id

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return -1
