"""Handles the SQL Read Commands for Managers safely"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Also use same read permissions as the superior's read permissions


def read_employees_given_warehouse(conn, warehouse_name=None, warehouse_id=None):
    """Given a warehouse, view a list of all employees based there"""

    if not warehouse_id and not warehouse_name:
        print("Invalid: Didn't provide employee name or id")
        return warehouse_id

    query_id = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s;
    """

    query_warehouse = """
        SELECT 
            e.name,
            e.employee_id
        FROM warehouse w
        LEFT OUTER JOIN employee e ON
            (w.warehouse_id = e.home_warehouse_id)
        WHERE w.warehouse_id = %s
        
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            if warehouse_name:
                print(f"\n--- Employee Information of {warehouse_name} ---")
                cur.execute(query_id, (warehouse_name,))
                possible_warehouse_id = cur.fetchone()
                if not possible_warehouse_id:
                    print("Name not found.")
                    return None
                warehouse_id = possible_warehouse_id["warehouse_id"]

            else:
                print(f"\n--- Employee Information of Warehouse #{warehouse_id} ---")

            cur.execute(query_warehouse, (warehouse_id,))
            results = cur.fetchall()
            if not results:
                print("No Employee Information.")
                return []
            array_result = []
            for s in results:
                array_result.append(
                    [
                        s["name"],
                        s["employee_id"],
                    ]
                )
                print(f"{s['employee_id']}: {s['name']}")
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_employees_without_warehouse(conn):
    """View a list of all employees not based in a warehouse"""

    query_warehouse = """
        SELECT 
            e.name,
            e.employee_id
        FROM employee e
        WHERE e.home_warehouse_id IS NULL
        
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            print("\n--- Employees Not Based IN Warehouse ---")
            cur.execute(query_warehouse)
            results = cur.fetchall()
            if not results:
                print("No Employee Information.")
                return []
            array_result = []
            for s in results:
                array_result.append(
                    [
                        s["name"],
                        s["employee_id"],
                    ]
                )
                print(f"{s['employee_id']}: {s['name']}")
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []
