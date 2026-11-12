"""Handles the SQL Write Commands for accounts and sessions safely"""

import psycopg2

from db.auth import (
    hash_password,
    hash_token,
    is_valid_password,
    new_session_token,
    verify_password,
)

SESSION_HOURS = 24


def write_signup_customer(conn, name, email, phone, username, password):
    """Creates a customer and their login together, returns the new user_id (None if it failed)"""
    if not is_valid_password(password):
        print("Invalid: Password must be 8+ characters (72 bytes max).")
        return None

    query_customer = """
        INSERT INTO customer (name, email, phone)
        VALUES (%s, %s, %s)
        RETURNING customer_id;
    """
    query_account = """
        INSERT INTO userAccount (username, password_hash, customer_id)
        VALUES (%s, %s, %s)
        RETURNING user_id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query_customer, (name, email, phone))
            customer_id = cur.fetchone()[0]
            cur.execute(
                query_account, (username, hash_password(password), customer_id)
            )
            user_id = cur.fetchone()[0]
        conn.commit()
        return user_id

    except psycopg2.errors.UniqueViolation:
        # Rolls back the customer insert too, so no orphaned customer is left behind
        conn.rollback()
        print(f"Invalid: Username '{username}' is already taken.")
        return None
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error while creating customer account: {e}")
        return None


def write_create_user(
    conn, username, password, is_admin=False, customer_id=None, employee_id=None
):
    """Creates a login (used by the admin), returns the new user_id (None if it failed).
    An admin has no profile; everyone else must link to exactly one customer or employee"""
    if not is_valid_password(password):
        print("Invalid: Password must be 8+ characters (72 bytes max).")
        return None

    query_employee = """
        SELECT 1
        FROM employee
        WHERE employee_id = %s AND (final_date IS NULL OR final_date >= CURRENT_DATE);
    """
    query_account = """
        INSERT INTO userAccount (username, password_hash, is_admin, customer_id, employee_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id;
    """
    try:
        with conn.cursor() as cur:
            if employee_id is not None:
                cur.execute(query_employee, (employee_id,))
                if not cur.fetchone():
                    print(f"Invalid: No active employee with ID {employee_id}.")
                    return None

            cur.execute(
                query_account,
                (username, hash_password(password), is_admin, customer_id, employee_id),
            )
            user_id = cur.fetchone()[0]
        conn.commit()
        return user_id

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("Invalid: Username is taken or that profile already has an account.")
        return None
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error while creating user: {e}")
        return None


def write_create_session(conn, user_id):
    """Starts a login session, returns the token to give the client (None if it failed)"""
    query_cleanup = """
        DELETE FROM userSession
        WHERE expires_at <= CURRENT_TIMESTAMP;
    """
    query_session = """
        INSERT INTO userSession (token_hash, user_id, expires_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP + %s * INTERVAL '1 hour');
    """
    token = new_session_token()
    try:
        with conn.cursor() as cur:
            cur.execute(query_cleanup)
            cur.execute(query_session, (hash_token(token), user_id, SESSION_HOURS))
        conn.commit()
        return token

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error while creating session: {e}")
        return None


def write_delete_session(conn, token):
    """Logs out by deleting the session, returns whether a session was removed"""
    query = """
        DELETE FROM userSession
        WHERE token_hash = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, (hash_token(token),))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error while deleting session: {e}")
        return False


def write_change_password(conn, user_id, old_password, new_password, keep_token=None):
    """Changes a password if the old one is correct and ends the user's other sessions,
    returns whether the password was changed"""
    if not is_valid_password(new_password):
        print("Invalid: Password must be 8+ characters (72 bytes max).")
        return False

    query_current = """
        SELECT password_hash
        FROM userAccount
        WHERE user_id = %s;
    """
    query_update = """
        UPDATE userAccount
        SET password_hash = %s
        WHERE user_id = %s;
    """
    query_sessions = """
        DELETE FROM userSession
        WHERE user_id = %s AND token_hash IS DISTINCT FROM %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query_current, (user_id,))
            row = cur.fetchone()
            if not row or not verify_password(old_password, row[0]):
                print("Invalid: Current password is incorrect.")
                return False

            cur.execute(query_update, (hash_password(new_password), user_id))
            keep_hash = hash_token(keep_token) if keep_token else None
            cur.execute(query_sessions, (user_id, keep_hash))
        conn.commit()
        return True

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error while changing password: {e}")
        return False
