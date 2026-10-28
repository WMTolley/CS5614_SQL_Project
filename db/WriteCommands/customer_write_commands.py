"""Handles the SQL Write Commands for Customer safely"""

import psycopg2


def write_create_customer_account(conn, name, email, phone, hashed_password):
    """Create a customer account"""

    if email is None and phone is None:
        return None

    if email is not None and "@" not in email:
        return None

    item_query = """
        INSERT INTO customer (name, email, phone, hashed_password) VALUES
        (%s, %s, %s, %s)
        RETURNING customer_id;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                item_query,
                (name, email, phone, hashed_password),
            )
            result = cur.fetchone()
            if not result:
                return None

            conn.commit()
            return result[0]

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None


def write_modify_customer_account(
    conn, customer_id, email=None, phone=None, hashed_password=None
):
    """Modify a customer account"""

    update_email_query = """
        UPDATE customer 
        SET email = %s
        WHERE customer_id = %s
        RETURNING customer_id;
    """

    update_phone_query = """
        UPDATE customer 
        SET phone = %s
        WHERE customer_id = %s
        RETURNING customer_id;
    """

    update_password_query = """
        UPDATE customer 
        SET hashed_password = %s
        WHERE customer_id = %s
        RETURNING customer_id;
    """

    try:
        with conn.cursor() as cur:
            updated_any = False

            if email:
                cur.execute(update_email_query, (email, customer_id))
                if cur.fetchone():
                    updated_any = True

            if phone:
                cur.execute(update_phone_query, (phone, customer_id))
                if cur.fetchone():
                    updated_any = True

            if hashed_password:
                cur.execute(update_password_query, (hashed_password, customer_id))
                if cur.fetchone():
                    updated_any = True

            if updated_any:
                conn.commit()
                return True

            return False

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return False
