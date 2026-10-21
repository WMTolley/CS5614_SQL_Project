"""Creates the Inventory SQL database (reinitializes the database)"""

from db.ReadCommands.customer_read_commands import (
    read_available_items_in_warehouse,
    read_item_stats_given_category_and_warehouse,
    read_item_stats_given_name_and_warehouse,
    read_number_available_for_item,
    read_ordered_items_in_warehouse,
    read_public_warehouses,
    read_soldout_unordered_items,
    read_supplier_count_of_available_item,
)
from db.ReadCommands.staff_read_commands import (
    read_ordered_items_in_warehouse,
    read_subordinates_of_employee,
    read_supervisors_of_employee,
)
from db.ReadCommands.superior_read_commands import (
    read_itemCount_given_warehouse,
    read_iteminfo_in_warehouse,
    read_statusChanges_of_employee,
    read_subordinates_of_named_employee,
)
from db.sql_commands import connect_and_init, show_items, show_statusChanges
from db.WriteCommands.manager_write_commands import (
    write_delete_warehouse,
    write_new_warehouse,
    write_warehouse_privacy,
)
from db.WriteCommands.staff_write_commands import (
    write_delivered_as_InStock,
    write_instock_as_unavailable,
)
from db.WriteCommands.superior_write_commands import write_order_item

if __name__ == "__main__":
    connection = connect_and_init("db/Data/schema.sql", "db/Data/seed.sql")
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

    read_subordinates_of_employee(connection, "1")
    read_subordinates_of_employee(connection, "2")
    read_supervisors_of_employee(connection, "4")
    read_supervisors_of_employee(connection, "1")

    read_available_items_in_warehouse(connection, "Washington DC Branch")
    read_soldout_unordered_items(connection, "Washington DC Branch")
    write_instock_as_unavailable(connection, 1, item_id="1")
    read_available_items_in_warehouse(connection, "Washington DC Branch")
    read_soldout_unordered_items(connection, "Washington DC Branch")
    show_statusChanges(connection)

    write_instock_as_unavailable(connection, 1, item_id="1")
    write_delivered_as_InStock(connection, 1, item_id="1")
    show_statusChanges(connection)

    read_ordered_items_in_warehouse(connection, "Washington DC Branch")
    write_delivered_as_InStock(connection, 3, item_id="4")
    show_statusChanges(connection)

    write_delivered_as_InStock(connection, 1, item_id="4")
    show_statusChanges(connection)
    read_ordered_items_in_warehouse(connection, "Washington DC Branch")

    read_subordinates_of_named_employee(connection, "Ezra Jedi")

    write_delivered_as_InStock(connection, 1, item_id="5")
    write_delivered_as_InStock(connection, 1, item_id="7")
    write_delivered_as_InStock(connection, 1, item_id="6")

    read_statusChanges_of_employee(connection, employee_id="3")

    read_statusChanges_of_employee(connection, employee_name="Ezra Jedi")

    read_itemCount_given_warehouse(connection, warehouse_id="1")

    read_itemCount_given_warehouse(connection, warehouse_name="Rundown Salon")

    read_iteminfo_in_warehouse(connection, warehouse_id="1")

    read_iteminfo_in_warehouse(connection, warehouse_name="Rundown Salon")

    read_statusChanges_of_employee(connection, employee_id="3")

    write_order_item(connection, "1", "AddedItem", "ADDITEM", 15.00, 2, 3)

    read_iteminfo_in_warehouse(connection, warehouse_id="2")

    read_statusChanges_of_employee(connection, employee_id="3")

    read_number_available_for_item(connection, "AddedItem")

    read_item_stats_given_name_and_warehouse(
        connection, "AddedItem", "Washington DC Branch"
    )
    write_delivered_as_InStock(connection, 1, item_id="21")

    show_items(connection)

    read_number_available_for_item(connection, "AddedItem")

    print(read_public_warehouses(connection))

    write_new_warehouse(connection, "Nice", "1294", "60623", True)

    print(read_public_warehouses(connection))

    write_warehouse_privacy(connection, 7, False)

    print(read_public_warehouses(connection))

    write_warehouse_privacy(connection, 7, True)

    print(read_public_warehouses(connection))

    write_delete_warehouse(connection, 7)

    print(read_public_warehouses(connection))

    write_delete_warehouse(connection, 6)

    print(read_public_warehouses(connection))

    # read_iteminfo_in_warehouse(connection, warehouse_id=2)

    connection.close()


#     ('Washington DC Branch', 'White House, Washington DC', true),
# ('DisneyLand Storage', 'DisneyLand, Florida', true),
# ('SciFi Moon Base', 'Moon', false);
# Rundown Salon
