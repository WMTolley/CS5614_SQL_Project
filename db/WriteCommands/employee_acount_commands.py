"""Handles the SQL Write Commands for Customer safely"""

import psycopg2

# TODO need addional commands for setting warehouse_Id and supervisor_id and also for chaning an employee_type/roletype


def write_create_employee_account(
    conn, name, email, phone, hashed_password, employee_type, role_type
):
    """Create an employee account"""

    # Guard clauses
    if email is None and phone is None:
        return None

    if email is not None and "@" not in email:
        return None

    if role_type is None:
        return None

    role_table_map = {
        "WarehouseStaff": "warehousestaff",
        "Supervisor": "supervisor",
        "InventoryManager": "inventorymanager",
    }

    if employee_type not in role_table_map:
        return None

    employee_query = """
        INSERT INTO employee (name, email, phone, hashed_password) 
        VALUES (%s, %s, %s, %s)
        RETURNING employee_id;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                employee_query,
                (name, email, phone, hashed_password),
            )
            result = cur.fetchone()
            if not result:
                return None

            employee_id = result[0]

            role_table = role_table_map[employee_type]
            role_query = f"""
                INSERT INTO {role_table} (employee_id, role_type) 
                VALUES (%s, %s);
            """
            cur.execute(role_query, (employee_id, role_type))

            conn.commit()
            return employee_id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return None


def write_modify_employee_account(
    conn,
    employee_id,
    name=None,
    email=None,
    phone=None,
    hashed_password=None,
):
    """
    Modify an employee account dynamically.
    """
    emp_fields = []
    emp_values = []

    if name is not None:
        emp_fields.append("name = %s")
        emp_values.append(name)
    if email is not None:
        if "@" not in email:
            return False
        emp_fields.append("email = %s")
        emp_values.append(email)
    if phone is not None:
        emp_fields.append("phone = %s")
        emp_values.append(phone)
    if hashed_password is not None:
        emp_fields.append("hashed_password = %s")
        emp_values.append(hashed_password)

    try:
        with conn.cursor() as cur:
            updated_any = False

            if emp_fields:
                emp_values.append(employee_id)
                emp_query = f"""
                    UPDATE employee 
                    SET {", ".join(emp_fields)} 
                    WHERE employee_id = %s;
                """
                cur.execute(emp_query, tuple(emp_values))
                if cur.rowcount > 0:
                    updated_any = True

            if updated_any:
                conn.commit()
                return True

            return False

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database error: {e}")
        return False
