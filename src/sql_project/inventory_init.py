"""Creates the Inventory SQL database (reinitializes the database)"""

from sql_project.sql_commands import connect_and_init, show_items

if __name__ == "__main__":
    connection = connect_and_init("Data/inventory_init.sql")
    show_items(connection)
    connection.close()
