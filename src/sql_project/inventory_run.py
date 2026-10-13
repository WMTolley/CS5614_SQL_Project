"""Creates the Inventory SQL database (reinitializes the database)"""

from sql_project.sql_commands import (
    connect_and_init,
    modify_items_categoryID_safely,
    show_items,
    show_items_with_category,
)

if __name__ == "__main__":
    connection = connect_and_init("Data/inventory_run.sql")
    show_items(connection)
    show_items_with_category(connection)
    modify_items_categoryID_safely(connection, 1, 2)
    show_items_with_category(connection)
    modify_items_categoryID_safely(connection, 1, None)
    show_items_with_category(connection)

    connection.close()

# Statuses:
# Non-Existant
# Ordered
# Delivered
# In Stock
# Reserved
# Unavailable
# Discarded
