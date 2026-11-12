"""Creates the first admin account from environment variables (no hardcoded password).
Run after the schema is loaded, since loading the schema drops every account."""

import os

import psycopg2

from db.WriteCommands.auth_write_commands import write_create_user


def ensure_admin(conn):
    """Creates the admin from ADMIN_USERNAME / ADMIN_PASSWORD if no admin exists yet,
    returns the new user_id (None if skipped or failed)"""
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")
    if not username or not password:
        print("WARNING: ADMIN_USERNAME / ADMIN_PASSWORD not set; no admin created.")
        return None

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM userAccount WHERE is_admin;")
            if cur.fetchone():
                return None
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error while checking for an admin: {e}")
        return None

    return write_create_user(conn, username, password, is_admin=True)
