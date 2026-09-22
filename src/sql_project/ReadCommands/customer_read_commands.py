"""Handles the SQL Read Commands for Customers safely"""

import psycopg2
from psycopg2.extras import RealDictCursor


def read_public_warehouses(conn) -> list:
    """Display the name, id, and location of each warehouse thats public"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print("\n--- Warehouses ---")
        cur.execute("""
            SELECT w.name, w.warehouse_id, w.location
            FROM warehouse w
            WHERE is_public;
        """)
        result = cur.fetchall()
        array_result = []
        for s in result:
            array_result.append([s["warehouse_id"], s["name"], s["location"]])
            print(f"{s['warehouse_id']}: {s['name']} ({s['location']})")
        return array_result
    return []


def read_available_items_in_warehouse(conn, warehouse_name) -> dict:
    """Display the name and id of each available item in a public warehouse"""
    query_warehouse = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s AND is_public;
    """

    query_items = """
        SELECT i.name, i.item_id
        FROM item i
        WHERE warehouse_id = %s AND status = 'In Stock';
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(query_warehouse, (warehouse_name,))
            warehouse_row = cur.fetchone()

            if not warehouse_row:
                print(f"\nInvalid: No warehouse found with name '{warehouse_name}'")
                return None

            warehouse_id = warehouse_row["warehouse_id"]

            print(f"\n--- Available Items in Warehouse ({warehouse_name}) ---")
            cur.execute(query_items, (warehouse_id,))
            items_rows = cur.fetchall()

            items = {}

            for row in items_rows:
                name = row["name"]
                serial = row["item_id"]

                if name not in items:
                    items[name] = []
                items[name].append(f"(#{serial})")

            if not items:
                print("No available items in this warehouse.")
                return {}

            for name, serial_list in items.items():
                serials_str = " ".join(serial_list)
                print(f"- {name} {serials_str}")

            return items

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return {}


def read_ordered_items_in_warehouse(conn, warehouse_name):
    """Display the set of names of the ordered item given a public warehouse"""
    query_warehouse = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s AND is_public;
    """

    query_items = """
        SELECT i.name
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

            print(f"\n--- Ordered Items for Warehouse ({warehouse_name}) ---")
            cur.execute(query_items, (warehouse_id,))
            items = cur.fetchall()

            seen_ids = set()
            unique_items = []

            for row in items:
                if row["name"] not in seen_ids:
                    unique_items.append(row["name"])
                    seen_ids.add(row["name"])

            if not unique_items:
                print("No available items in this warehouse.")
                return []

            for item in unique_items:
                print(f"- {item}")

            return unique_items

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_number_available_for_item(conn, item_name) -> dict:
    """Display the corresponding warehouse_name and count of the speicified item"""
    query_warehouse = """
        SELECT 
            w.name AS warehouse_name, 
            COALESCE(COUNT(i.name), 0) AS stock_count 
        FROM warehouse w 
        LEFT JOIN item i 
            ON w.warehouse_id = i.warehouse_id 
            AND i.status = 'In Stock' 
            AND i.name = %s
        WHERE w.is_public
        GROUP BY w.warehouse_id, w.name
        
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print(f"\n--- Number of {item_name}(s) ---")
            cur.execute(query_warehouse, (item_name,))
            result = cur.fetchall()

            dictionary_result = {}
            for s in result:
                print(f"{s['warehouse_name']}: {s['stock_count']}")
                dictionary_result[s["warehouse_name"]] = s["stock_count"]
            return dictionary_result
    except psycopg2.Error as e:
        print(f"ERROR: Database error while processing lookup: {e}")
        conn.rollback()
        return []


def read_soldout_unordered_items(conn, warehouse_name) -> list:
    """Display the name, and last ordered date of each souldout, unordered item in a public warehouse"""
    query_warehouse = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s AND is_public;
    """

    query_items = """WITH soldout_items AS (
        SELECT DISTINCT name
        FROM item
        WHERE status IN ('Unavailable', 'Reserved')
        AND warehouse_id = %s
        AND name NOT IN (
            SELECT name 
            FROM item 
            WHERE status IN ('Ordered', 'In Stock')
            AND warehouse_id = %s
        )
        ),

        possible_latest_supplied AS (
            SELECT i.item_id, i.name, i.status
            FROM item i
            JOIN soldout_items u ON i.name = u.name
            WHERE i.warehouse_id = %s
        ),

        names_to_date AS (
            SELECT j.name, k.date_supplied
            FROM possible_latest_supplied j
            JOIN supply k on j.item_id = k.item_id
        )

        SELECT MAX(date_supplied) as latestTimestamp, name
        FROM names_to_date
        GROUP BY name;"""

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(query_warehouse, (warehouse_name,))
            warehouse_row = cur.fetchone()

            if not warehouse_row:
                print(f"\nInvalid: No warehouse found with name '{warehouse_name}'")
                return None

            warehouse_id = warehouse_row["warehouse_id"]

            print(f"\n--- Unavailable Items in Warehouse ({warehouse_name}) ---")
            cur.execute(query_items, (warehouse_id, warehouse_id, warehouse_id))
            items_rows = cur.fetchall()

            if len(items_rows) <= 0:
                print("None Found")
                return []

            items = []

            for row in items_rows:
                name = row["name"]
                time = row["latesttimestamp"]
                items.append([name, time])
                print(f"- {name} [{time}]")

            return items

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_supplier_count_of_available_item(conn, item_name) -> dict:
    """Display the department and name of the suppliers for an item"""
    query_warehouse = """
        SELECT 
            w.name as warehouse_name,
            k.name
        FROM warehouse w 
        LEFT JOIN item i 
            ON w.warehouse_id = i.warehouse_id 
            AND i.status = 'In Stock' 
            AND i.name = %s
        LEFT JOIN supply j 
            ON j.item_id = i.item_id 
        LEFT JOIN supplier k
            ON j.supplier_id = k.supplier_id 
        WHERE w.is_public
        
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print(f"\n--- Suppliers of {item_name}(s) ---")
            cur.execute(query_warehouse, (item_name,))
            result = cur.fetchall()
            dictionary_result = {}
            for s in result:
                warehouse = s["warehouse_name"]
                supplier = s["name"]
                if warehouse not in dictionary_result:
                    dictionary_result[warehouse] = []
                dictionary_result[warehouse].append(f"{supplier}")
            for s, j in dictionary_result.items():
                print(f"{s}")
                for k in j:
                    print(f"- {k}")
            # print(dictionary_result)
            return dictionary_result
    except psycopg2.Error as e:
        print(f"ERROR: Database error while processing lookup: {e}")
        conn.rollback()
        return []


def read_item_stats_given_name_and_warehouse(conn, item_name, warehouse_name) -> list:
    """Displays the name, serial_number, markup_price,category_id for a given item in a given warehouse"""

    query_warehouse = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s AND is_public;
    """

    query_items = """
        SELECT i.serial_number, i.markup_price, k.name as supplier_name, i.item_id
        FROM item i
        LEFT JOIN supply j 
            ON j.item_id = i.item_id
        LEFT JOIN supplier k
            ON j.supplier_id = k.supplier_id
        WHERE warehouse_id = %s AND status = 'In Stock' AND i.name = %s;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(query_warehouse, (warehouse_name,))
            warehouse_row = cur.fetchone()

            if not warehouse_row:
                print(f"\nInvalid: No warehouse found with name '{warehouse_name}'")
                return None

            warehouse_id = warehouse_row["warehouse_id"]

            print(f"\n--- Info of {item_name}(s) in ({warehouse_name}) ---")
            cur.execute(query_items, (warehouse_id, item_name))
            items_rows = cur.fetchall()

            if len(items_rows) <= 0:
                print("None Found")
                return []

            items = []

            for row in items_rows:
                serial = row["serial_number"]
                price = row["markup_price"]
                supplier = row["supplier_name"]
                id = row["item_id"]

                items.append([price, supplier, serial])
                print(f"- ${price} | {supplier} | {serial} (#{id})")

            return items

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []


def read_item_stats_given_category_and_warehouse(
    conn, category_name, warehouse_name
) -> list:
    """Displays the name, serial_number, markup_price,category_id for a given item in a given warehouse"""

    query_warehouse = """
        SELECT w.warehouse_id
        FROM warehouse w
        WHERE name = %s AND is_public;
    """

    query_category = """
        SELECT w.category_id
        FROM itemCategory w
        WHERE name = %s;
    """

    query_items = """
        SELECT i.serial_number, i.markup_price, k.name as supplier_name, i.name as item_name, i.item_id
        FROM item i
        LEFT JOIN supply j 
            ON j.item_id = i.item_id
        LEFT JOIN supplier k
            ON j.supplier_id = k.supplier_id
        WHERE warehouse_id = %s AND status = 'In Stock' AND i.category_id = %s;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(query_warehouse, (warehouse_name,))
            warehouse_row = cur.fetchone()

            if not warehouse_row:
                print(f"\nInvalid: No warehouse found with name '{warehouse_name}'")
                return None

            warehouse_id = warehouse_row["warehouse_id"]
            cur.execute(query_category, (category_name,))
            category_row = cur.fetchone()

            if not category_row:
                print(f"\nInvalid: No warehouse found with name '{warehouse_name}'")
                return None

            category_id = category_row["category_id"]
            print(f"\n--- Info of all {category_name}(s) in ({warehouse_name}) ---")
            cur.execute(query_items, (warehouse_id, category_id))
            items_rows = cur.fetchall()

            if len(items_rows) <= 0:
                print("None Found")
                return []

            items = []

            for row in items_rows:
                name = row["item_name"]
                serial = row["serial_number"]
                price = row["markup_price"]
                supplier = row["supplier_name"]
                id = row["item_id"]

                items.append([name, price, supplier, serial])
                print(f"- {name} | ${price} | {supplier} | {serial} ({id})")

            return items

        except psycopg2.Error as e:
            print(f"ERROR: Database error while processing lookup: {e}")
            conn.rollback()
            return []
