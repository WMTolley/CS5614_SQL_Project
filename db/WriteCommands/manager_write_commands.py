"""Handles the SQL Write Commands for Manager safely"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Same write permissions as the warehouse staff’s write permissions.
# Same write permissions as the supervisor’s write permissions


def write_new_warehouse(conn, name: str, street: str, zip: str, is_public: bool):
    """Add new warehouse"""

    item_query = """
        INSERT INTO warehouse (name, street, zip, is_public) VALUES
        (%s, %s, %s, %s)
        RETURNING warehouse_id;
    """

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                item_query,
                (
                    name,
                    street,
                    zip,
                    is_public,
                ),
            )
            result = cur.fetchone()
            if not result:
                return

            conn.commit()
            id = result["warehouse_id"]
            return id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return


def write_warehouse_privacy(conn, warehouse_id: int, is_public: bool):
    """Set a warehouse's privacy as either public or private"""

    item_query = """
        UPDATE warehouse
        SET is_public = %s
        WHERE warehouse_id = %s
        RETURNING name;
    """

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                item_query,
                (
                    is_public,
                    warehouse_id,
                ),
            )
            result = cur.fetchone()
            if not result:
                return

            conn.commit()
            id = result["name"]
            return id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return


def write_delete_warehouse(conn, warehouse_id: int):
    """Delete an empty warehouse"""

    item_query = """
        DELETE FROM warehouse
        WHERE warehouse_id = %s
        RETURNING name;
    """

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                item_query,
                (warehouse_id,),
            )
            result = cur.fetchone()
            if not result:
                return

            conn.commit()
            id = result["name"]
            return id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return
