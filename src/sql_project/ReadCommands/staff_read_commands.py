"""Handles the SQL Read Commands for Staff safely"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Also use same read permissions as the consumer's read permissions


def read_subordinates_of_employee(conn, employee_id):
    """Display the subordinates that supervise a given employee_id"""
    query_warehouse = """
        SELECT w.employee_id
        FROM employee w
        WHERE supervisor_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print(f"\n--- Subordinates of {employee_id} ---")
        try:
            cur.execute(query_warehouse, (employee_id,))
            employee_ids = cur.fetchall()
            if not employee_ids:
                print("No suborbinates.")
                return []

            array_result = []
            for s in employee_ids:
                array_result.append([s["employee_id"]])
                print(f"- Employee ID: {s['employee_id']}")
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return {}


def read_supervisors_of_employee(conn, employee_id):
    """Display the subordinates that supervise a given employee_id"""
    query_warehouse = """
        SELECT w.supervisor_id
        FROM employee w
        WHERE employee_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # print(f"\n--- Subordinates of {employee_id} ---")
        try:
            cur.execute(query_warehouse, (employee_id,))
            employee_ids = cur.fetchone()

            if not employee_ids:
                print(f"No supervisor of '{employee_id}'")
                return None

            supervisor_id = employee_ids["supervisor_id"]
            print(
                f"\nSupervisor with Employee ID: {employee_id} is employee with Employee ID: {supervisor_id}"
            )
            return supervisor_id

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return {}


def read_ordered_items_in_warehouse(conn, warehouse_name):
    query_warehouse = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s AND is_public;
    """

    query_items = """
        SELECT i.name, i.item_id
        FROM item i
        WHERE warehouse_id = %s AND status = 'Ordered';
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(query_warehouse, (warehouse_name,))
            warehouse_row = cur.fetchone()

            if not warehouse_row:
                print(f"\nInvalid: No warehouse found with name '{warehouse_name}'")
                return None

            warehouse_id = warehouse_row["warehouse_id"]

            print(f"\n--- Ordered Items in ({warehouse_name}) ---")
            cur.execute(query_items, (warehouse_id,))
            items_rows = cur.fetchall()

            if len(items_rows) <= 0:
                print("None Found")
                return []

            items = []

            for row in items_rows:
                name = row["name"]
                id = row["item_id"]

                items.append([name, id])
                print(f"- {name} (#{id})")

            return items

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []
