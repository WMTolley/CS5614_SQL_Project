"""Handles the SQL Write Commands for Superior safely"""

from datetime import datetime

import psycopg2


def write_order_item(
    conn, warehouse_id, name, serial_number, markup_price, category_id, employee_id
):
    """Add new items (the current status would be marked as “ordered”, status change would go from "Non-Existant" to "Ordered")"""

    item_query = """
        INSERT INTO item (name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
        (%s, %s, %s, %s, %s, %s)
        RETURNING item_id;
    """

    status_query = """
        INSERT INTO statusChange (old_status, new_status, changed_at, item_id, employee_id) VALUES
        (%s, %s, %s, %s, %s);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                item_query,
                (
                    name,
                    serial_number,
                    "Ordered",
                    markup_price,
                    category_id,
                    warehouse_id,
                ),
            )
            result = cur.fetchone()
            # conn.commit()
            if not result:
                return

            cur.execute(
                status_query,
                (
                    "Non-Existant",
                    "Ordered",
                    datetime.now(),
                    result[0],
                    employee_id,
                ),
            )

            conn.commit()
            return result[0]

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return


def write_ordered_as_delivered(conn, employee_id, item_serial=None, item_id=None):
    """Mark an item that’s current status is “Ordered” as “Delivered”."""

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
        SET status = 'Delivered'
        WHERE item_id = %s
        AND status = 'Ordered'
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
                    ("Ordered", "Delivered", item_id, employee_id),
                )
            conn.commit()
            return item_id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None


def write_instock_as_reserved(conn, employee_id, item_serial=None, item_id=None):
    """Mark an item that’s current status is "In Stock" as “Reserved”"""

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
        SET status = 'Reserved'
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
                    ("In Stock", "Reserved", item_id, employee_id),
                )
            conn.commit()
            return item_id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None


def write_motify_markup_price(conn, new_price, item_serial=None, item_id=None):
    """Edit an item’s markup price."""

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
        SET markup_price = %s
        WHERE item_id = %s
        AND status = 'In Stock'
        RETURNING item_id;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    new_price,
                    item_id,
                ),
            )
            result = cur.fetchone()
            conn.commit()
            return result[0] if result else None

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None
