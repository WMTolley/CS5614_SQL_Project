"""Handles the SQL Write Commands for Staff safely"""

import psycopg2


def write_instock_as_unavailable(conn, employee_id, item_serial=None, item_id=None):
    """Modify the item with the specified itemID or ItemSerial thats instock to unavailable"""

    if not item_serial and not item_id:
        print("Invalid: Didn't provide serial or id")
        return item_id

    if not item_id:
        query_id = """
            SELECT i.item_id
            FROM item i
            WHERE serial_number = %s;
        """
        try:
            with conn.cursor() as cur:
                cur.execute(query_id, (item_serial,))
                result = cur.fetchone()
                conn.commit()
                if not result:
                    print(f"Invalid: No item with this serial: {item_serial}")
                    return None
                item_id = result["item_id"]

        except psycopg2.Error as e:
            conn.rollback()
            print(f"ERROR: Database error: {e}")
            return None

    query = """
        UPDATE item 
        SET status = 'Unavailable'
        WHERE item_id = %s
        AND status = 'In Stock'
        RETURNING item_id;
    """

    query_add_statuschange = """
        INSERT INTO statusChange (old_status, new_status, item_id, employee_id) 
        VALUES (%s, %s, %s, %s)
        RETURNING new_status;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, (item_id,))
            result = cur.fetchone()
            if result:
                cur.execute(
                    query_add_statuschange,
                    ("In Stock", "Unavailable", item_id, employee_id),
                )
            conn.commit()
            return item_id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None


def write_delivered_as_InStock(conn, employee_id, item_serial=None, item_id=None):
    """Modify the item with the specified itemID or ItemSerial thats delivered to In Stock"""

    if not item_serial and not item_id:
        print("Invalid: Didn't provide serial or id")
        return item_id

    if not item_id:
        query_id = """
            SELECT i.item_id
            FROM item i
            WHERE serial_number = %s;
        """
        try:
            with conn.cursor() as cur:
                cur.execute(query_id, (item_serial,))
                result = cur.fetchone()
                conn.commit()
                if not result:
                    print(f"Invalid: No item with this serial: {item_serial}")
                    return None
                item_id = result["item_id"]

        except psycopg2.Error as e:
            conn.rollback()
            print(f"ERROR: Database error: {e}")
            return None

    query = """
        UPDATE item 
        SET status = 'In Stock'
        WHERE item_id = %s
        AND status = 'Delivered'
        RETURNING item_id;
    """

    query_add_statuschange = """
        INSERT INTO statusChange (old_status, new_status, item_id, employee_id) 
        VALUES (%s, %s, %s, %s)
        RETURNING new_status;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(query, (item_id,))
            result = cur.fetchone()

            if result:
                cur.execute(
                    query_add_statuschange,
                    ("Delivered", "In Stock", item_id, employee_id),
                )
            conn.commit()
            return item_id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None
