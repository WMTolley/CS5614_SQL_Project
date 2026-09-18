"""Handles the SQL Read/Write Commands safely"""

import time

import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration Credentials for Database Container
DB_CONFIG = {
    "host": "db",
    "database": "devdb",
    "user": "devuser",
    "password": "devpassword",
    "port": 5432,
}


# Exampe Function (TODO: Remove Later)
def add_student_safely(conn, first_name, last_name, email):
    """Adds a student without risk of an injection attack"""
    query = """
        INSERT INTO students (first_name, last_name, email) 
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING -- Prevents crashes on duplicate entries
        RETURNING student_id;
    """
    with conn.cursor() as cur:
        cur.execute(query, (first_name, last_name, email))
        result = cur.fetchone()
        conn.commit()
        return result[0] if result else None


# Exampe Function (TODO: Remove Later)
def remove_student_safely(conn, student_id):
    """Deletes a student by their ID safely"""
    query = """
        DELETE FROM students 
        WHERE student_id = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, (student_id,))
            if cur.rowcount == 0:
                print(
                    f"Warning: No student found with ID {student_id}. Nothing was deleted."
                )
            else:
                print(
                    f"Successfully removed Student ID {student_id} and all their linked profiles/enrollments."
                )

        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Failed to delete student: {e}")


def connect_and_init(sql_path):
    """Attempt 5 times to connect after DB container initialization"""
    for _ in range(5):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur, open(sql_path, "r", encoding="utf-8") as f:
                cur.execute(f.read())
            conn.commit()
            return conn
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("ERROR: Database container not reachable.")


# Exampe Function (TODO: Remove Later)
def demonstrate_relationships(conn):
    """Example demonstration"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Demonstrate 1:1
        print("\n--- [1:1 Relationship] Student Profiles ---")
        cur.execute("""
            SELECT s.first_name, s.last_name, p.emergency_contact 
            FROM students s 
            JOIN student_profiles p ON s.student_id = p.student_id
        """)
        for r in cur.fetchall():
            print(
                f"{r['first_name']} {r['last_name']} | Emergency: {r['emergency_contact']}"
            )

        # Demonstrate 1:M
        print("\n--- [1:M Relationship] Departments and Their Courses ---")
        cur.execute("""
            SELECT d.name AS dept_name, c.course_code, c.title 
            FROM departments d
            LEFT JOIN courses c ON d.department_id = c.department_id
        """)
        for r in cur.fetchall():
            print(f"{r['dept_name']} -> [{r['course_code']}] {r['title']}")

        # Demonstrate M:M
        print("\n--- [M:M Relationship] Enrollments Map ---")
        cur.execute("""
            SELECT s.first_name, c.course_code, r.name AS dept_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses c ON e.course_id = c.course_id
            JOIN departments r ON c.department_id = r.department_id
        """)
        for r in cur.fetchall():
            print(
                f"Student {r['first_name']} is taking {r['course_code']} (Managed by: {r['dept_name']})"
            )


# Exampe Function (TODO: Remove Later)
def show_students(conn):
    """Display each students name in student table"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print("\n--- Students ---")
        cur.execute("""
            SELECT s.first_name, s.last_name
            FROM students s
        """)
        for s in cur.fetchall():
            print(f"{s['first_name']} {s['last_name']}")


# Exampe Function (TODO: Remove Later)
def get_studentids_from_firstname_safely(conn, first_name):
    """Retrieves all matching student IDs by their first name safely"""
    query = """
    SELECT student_id 
    FROM students 
    WHERE first_name = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, (first_name,))
            results = cur.fetchall()
            return [row[0] for row in results]

    except psycopg2.Error as e:
        print(f"ERROR: Database error while looking up student IDs: {e}")
        return []


def show_items(conn):
    """Display each items name in item table"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print("\n--- Items ---")
        cur.execute("""
            SELECT s.item_id, s.name
            FROM item s
        """)
        for s in cur.fetchall():
            print(f"{s['item_id']}: {s['name']}")


def show_items_with_category(conn):
    """Display each item's id and name along with its category name"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print("\n--- Items with Categories ---")
        cur.execute("""
            SELECT 
                i.item_id, 
                i.name, 
                c.name AS category_name
            FROM item i
            LEFT JOIN itemCategory c ON i.category_id = c.category_id;
        """)
        for row in cur.fetchall():
            category = row["category_name"] if row["category_name"] else "No Category"
            print(f"ID {row['item_id']} | Name: {row['name']} | Category: {category}")


def modify_items_categoryID_safely(conn, itemID, categoryID):
    """Modify the item with the specified itemID categoryID value"""
    query = """
        UPDATE item 
        SET category_id = %s 
        WHERE item_id = %s
        RETURNING name;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, (categoryID, itemID))
            result = cur.fetchone()
            conn.commit()
            return result[0] if result else None

    except Exception as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None
