# def write_modify_items_price_safely(conn, itemID, price, employee=None):
#     """Modify the item with the specified itemID price value"""

#     query = """
#         UPDATE item
#         SET markup_price = %s
#         WHERE item_id = %s
#         RETURNING name;
#     """
#     try:
#         with conn.cursor() as cur:
#             cur.execute(query, (price, itemID))
#             result = cur.fetchone()
#             conn.commit()
#             return result[0] if result else None

#     except psycopg2.Error as e:
#         conn.rollback()
#         print(f"ERROR: Database error: {e}")
#         return None
