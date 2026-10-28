"""Handles the SQL Read Commands for logging in and sessions safely"""

import psycopg2
from psycopg2.extras import RealDictCursor

from db.auth import hash_token, verify_password

_USER_SELECT = """
    SELECT u.user_id, u.username, u.password_hash, u.is_admin,
           u.customer_id, u.employee_id, e.employee_type, e.final_date,
           CURRENT_DATE AS today
    FROM userAccount u
    LEFT JOIN employee e ON e.employee_id = u.employee_id
"""


def _row_to_user(row) -> dict:
    """Builds the user dict the backend uses for permission checks (never includes the hash)"""
    if row["is_admin"]:
        role = "Admin"
    elif row["customer_id"] is not None:
        role = "Customer"
    else:
        role = row["employee_type"]
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "role": role,
        "is_admin": row["is_admin"],
        "customer_id": row["customer_id"],
        "employee_id": row["employee_id"],
    }


def _is_terminated(row) -> bool:
    """An employee whose final date has passed can no longer log in"""
    return row["final_date"] is not None and row["final_date"] < row["today"]


def read_login(conn, username, password):
    """Returns the user dict if the username/password are valid, otherwise None"""
    query = _USER_SELECT + "WHERE lower(u.username) = lower(%s);"
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (username,))
            row = cur.fetchone()

        if not row or not verify_password(password, row["password_hash"]):
            return None
        if _is_terminated(row):
            return None
        return _row_to_user(row)

    except psycopg2.Error as e:
        print(f"ERROR: Database error while processing login: {e}")
        conn.rollback()
        return None


def read_session_user(conn, token):
    """Returns the user dict for a valid, unexpired session token, otherwise None"""
    query = (
        _USER_SELECT
        + """
        JOIN userSession s ON s.user_id = u.user_id
        WHERE s.token_hash = %s AND s.expires_at > CURRENT_TIMESTAMP;
        """
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (hash_token(token),))
            row = cur.fetchone()

        if not row or _is_terminated(row):
            return None
        return _row_to_user(row)

    except psycopg2.Error as e:
        print(f"ERROR: Database error while processing session lookup: {e}")
        conn.rollback()
        return None
