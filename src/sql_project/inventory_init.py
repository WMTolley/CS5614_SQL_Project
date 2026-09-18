"""Creates the Inventory SQL database (reinitializes the database)"""

from sql_project.ReadCommands.customer_read_commands import (
    read_available_items_in_warehouse,
    read_item_stats_given_category_and_warehouse,
    read_item_stats_given_name_and_warehouse,
    read_number_available_for_item,
    read_ordered_items_in_warehouse,
    read_public_warehouses,
    read_soldout_unordered_items,
    read_supplier_count_of_available_item,
)
from sql_project.sql_commands import connect_and_init, show_items

if __name__ == "__main__":
    connection = connect_and_init("Data/inventory_init.sql")
    show_items(connection)
    read_public_warehouses(connection)
    read_available_items_in_warehouse(connection, "Washington DC Branch")
    read_ordered_items_in_warehouse(connection, "Washington DC Branch")
    read_number_available_for_item(connection, "Office Lamp")
    read_number_available_for_item(connection, "50ft Extension Cord")
    read_soldout_unordered_items(connection, "Rundown Salon")
    read_supplier_count_of_available_item(connection, "Office Lamp")
    read_item_stats_given_name_and_warehouse(connection, "Office Lamp", "Rundown Salon")
    read_item_stats_given_name_and_warehouse(
        connection, "Office Lamp", "Washington DC Branch"
    )
    read_item_stats_given_category_and_warehouse(
        connection, "Electronics", "Washington DC Branch"
    )
    connection.close()


#     ('Washington DC Branch', 'White House, Washington DC', true),
# ('DisneyLand Storage', 'DisneyLand, Florida', true),
# ('SciFi Moon Base', 'Moon', false);
# Rundown Salon
