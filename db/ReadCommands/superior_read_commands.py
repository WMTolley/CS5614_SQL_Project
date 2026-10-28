"""Handles the SQL Read Commands for Superiors safely"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Also use same read permissions as the staff's read permissions


def read_subordinates_of_named_employee(conn, employee_name):
    """Display the subordinates that supervise a given employee_name"""

    query_name = """
        SELECT w.employee_id
        FROM employee w
        WHERE name = %s;
    """

    query_warehouse = """
        SELECT w.name
        FROM employee w
        WHERE supervisor_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print(f"\n--- Subordinates of {employee_name} ---")
        try:
            cur.execute(query_name, (employee_name,))
            possible_supervisor_id = cur.fetchone()
            if not possible_supervisor_id:
                print("Name not found.")
                return None
            supervisor_id = possible_supervisor_id["employee_id"]

            cur.execute(query_warehouse, (supervisor_id,))
            subordinates_names = cur.fetchall()
            if not subordinates_names:
                print("No suborbinates.")
                return []

            array_result = []
            for s in subordinates_names:
                array_result.append(s["name"])
                print(f"- {s['name']}")
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_statusChanges_of_employee(conn, employee_name=None, employee_id=None):
    """Display the status changes of a given employee"""

    if not employee_name and not employee_id:
        print("Invalid: Didn't provide employee name or id")
        return None

    query_id = """
        SELECT w.employee_id
        FROM employee w
        WHERE name = %s;
    """

    query_statusChanges = """
        SELECT s.old_status, s.new_status, s.item_id, s.changed_at
        FROM statusChange s
        WHERE employee_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            if employee_name:
                print(f"\n--- Status Changes of {employee_name} ---")
                cur.execute(query_id, (employee_name,))
                possible_employee_id = cur.fetchone()
                if not possible_employee_id:
                    print("Name not found.")
                    return None
                employee_id = possible_employee_id["employee_id"]

            else:
                print(f"\n--- Status Changes of Employee #{employee_id} ---")

            cur.execute(query_statusChanges, (employee_id,))
            subordinates_names = cur.fetchall()
            if not subordinates_names:
                print("No Status Changes.")
                return []
            array_result = []
            for s in subordinates_names:
                array_result.append(
                    [
                        s["old_status"],
                        s["new_status"],
                        s["item_id"],
                        s["changed_at"],
                    ]
                )
                print(
                    f"'{s['old_status']}' to '{s['new_status']}' (item #{s['item_id']}) on [{s['changed_at']}]"
                )
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_itemCount_given_warehouse(conn, warehouse_name=None, warehouse_id=None):
    """Display the item count and last ordered date of every item of a given warehouse"""

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
            i.name, 
            COUNT(CASE WHEN i.status = 'In Stock' THEN 1 END) AS stock_count, 
            MAX(s.date_supplied) AS LastestOrdered 
        FROM item i 
        LEFT OUTER JOIN supply s ON (i.item_id = s.item_id) 
        WHERE i.warehouse_id = %s 
        GROUP BY i.name 
        ORDER BY LastestOrdered DESC
        
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            if warehouse_name:
                print(f"\n--- Supply Information of {warehouse_name} ---")
                cur.execute(query_id, (warehouse_name,))
                possible_warehouse_id = cur.fetchone()
                if not possible_warehouse_id:
                    print("Name not found.")
                    return []
                warehouse_id = possible_warehouse_id["warehouse_id"]

            else:
                print(f"\n--- Supply Information of Warehouse #{warehouse_id} ---")

            cur.execute(query_warehouse, (warehouse_id,))
            results = cur.fetchall()
            if not results:
                print("No Supplies Information.")
                return []
            array_result = []
            for s in results:
                array_result.append(
                    [
                        s["name"],
                        s["stock_count"],
                        s["lastestordered"],
                    ]
                )
                print(
                    f"{s['name']}: {s['stock_count']} (Last Supplied on [{s['lastestordered']}])"
                )
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_iteminfo_in_warehouse(conn, warehouse_name=None, warehouse_id=None) -> list:
    """Display various item info for every item of a given warehouse"""

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
            i.name,
            i.status,
            supplier.name AS supplier,
            supply.purchase_cost AS cost,
            i.markup_price
        FROM item i
        LEFT OUTER JOIN supply supply ON
            (i.item_id = supply.item_id)
        LEFT OUTER JOIN supplier supplier ON
            (supply.supplier_id = supplier.supplier_id)
        WHERE i.warehouse_id = %s
        ORDER BY i.name

    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            if warehouse_name:
                print(f"\n--- Items Information of {warehouse_name} ---")
                cur.execute(query_id, (warehouse_name,))
                possible_warehouse_id = cur.fetchone()
                # print(possible_warehouse_id)
                if not possible_warehouse_id:
                    print("Name not found.")
                    return []
                warehouse_id = possible_warehouse_id["warehouse_id"]

            else:
                print(f"\n--- Items Information of Warehouse #{warehouse_id} ---")

            cur.execute(query_warehouse, (warehouse_id,))
            results = cur.fetchall()
            if not results:
                print("No Supplies Information.")
                return []
            array_result = []
            for s in results:
                array_result.append(
                    [
                        s["name"],
                        s["status"],
                        s["supplier"],
                        s["cost"],
                        s["markup_price"],
                    ]
                )
                print(
                    f"{s['name']} ({s['status']}): From {s['supplier']} [{s['cost']} -> {s['markup_price']}]"
                )
            return array_result

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []
