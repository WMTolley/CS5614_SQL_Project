"""Creates the Inventory SQL database (reinitializes the database)"""

from db.sql_commands import (
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

# Timeline of item entity:

# Manager creates warehouse (whose privacy may be edited by a Manager, and if empty also deleted)
# Manager/Supervisor creates supplier (which can be deleted/modified only by a Manager/Supervisor)
# Manager/Supervisor creates itemCategory (which can only be modified/deleted by a supervisor/Manager)
# Manager/Supervisor creates item (with valid warehouseID)
# Manager/Supervisor creates supply
# Manager/Supervisor creates status Change (Non-Existant -> Ordered)
# Manager/Supervisor when delivered motifies status Change (Ordered -> Delivered)

# Staff (and only staff, so at least two people independly verify) modify an items status (Delivered -> In Stock)
# Manager/Supervisor can edit an Ordered/Delivered/InStock items markup price
# Any of the following three routes can occur:
# 1. Manager/Supervisor can modify a status change from In-Stock to Reserved if in a public warehouse
# 2. Manager/Supervisor/Staff can modify a status change from In-Stock to Unavailable (by selling to customer) if in a public warehouse
# 3. Manager can modify a status change from In-Stock or Reserved to Discarded and viceversa
# 4. Manager can transfer an item from one warehouse to another


# Customer Entity:
# Customers can create or modify a customer entity

# employee:
# Supervisor can create a employee ID
# Some fields can be modified by employee
# Some fields can be modified by Manager
#

# Transfer entity:
# Create when customer reserves item
# Create when customer buys/receives item
# If the customer hasn't received the item, the reservation can be deleted w/ status change

# Return entity:
# Create by employee when customer returns an item that was received

# Following entities can be created or deleted
# warehouseStaff (role can also be modified)
# supervisor
# inventoryManager

# management entity:
# Can be created, modified, or deleted
