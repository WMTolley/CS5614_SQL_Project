import datetime
from decimal import Decimal

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
from sql_project.sql_commands import (
    connect_and_init_safely,
)


def test_readPublicWarehouses():
    """Tests that read_public_warehouses correctly sees all public warehouses"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_public_warehouses(connection)
        expectation = [
            [1, "Hawaii Depo", "Hawaii, USA"],
            [2, "Alaska Station", "Alaska, USA"],
            [3, "Big Ben", "Big Ben, UK"],
            [4, "Antarctica Ace", "Antarctica"],
        ]
        assert result == expectation
    finally:
        connection.close()


def test_readAvailableItemsInWarehouse():
    """Tests that read_available_items_in_warehouse correctly sees available items in a given warehouse"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_available_items_in_warehouse(connection, "Invalid Warehouse")
        expectation = None
        assert result == expectation

        result = read_available_items_in_warehouse(connection, "Hawaii Depo")
        expectation = {}
        assert result == expectation

        result = read_available_items_in_warehouse(connection, "Alaska Station")
        expectation = {
            "Quantum Core Switch": ["10"],
        }
        assert result == expectation

        result = read_available_items_in_warehouse(connection, "Big Ben")
        expectation = {
            "Inaccessible Drill Rig": ["23"],
            "Quantum Core Switch": ["12", "13", "14"],
            "High-Vis Jackets (Bulk)": ["17"],
            "Smart Logistics Scanners": ["21", "22"],
        }
        assert result == expectation

    finally:
        connection.close()


def test_readOrderedItemsInWarehouse():
    """Tests that read_ordered_items_in_warehouse correctly sees ordered items in a given warehouse"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_ordered_items_in_warehouse(connection, "Invalid Warehouse")
        expectation = None
        assert result == expectation

        result = read_ordered_items_in_warehouse(connection, "Shadow Depot")
        expectation = None
        assert result == expectation

        result = read_ordered_items_in_warehouse(connection, "Hawaii Depo")
        expectation = []
        assert result == expectation

        result = read_ordered_items_in_warehouse(connection, "Alaska Station")
        expectation = []
        assert result == expectation

        result = read_ordered_items_in_warehouse(connection, "Big Ben")
        expectation = ["Industrial Conveyor Belt"]
        assert result == expectation

        result = read_ordered_items_in_warehouse(connection, "Antarctica Ace")
        expectation = ["Deep-Ice Drill Bit", "Extreme Weather Drysuit"]
        assert result == expectation

    finally:
        connection.close()


def test_readNumberAvailableForItem():
    """Tests that read_number_available_for_item correctly counts the number of items in each public warehouse"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_number_available_for_item(connection, "Invalid Name")
        expectation = {
            "Big Ben": 0,
            "Antarctica Ace": 0,
            "Alaska Station": 0,
            "Hawaii Depo": 0,
        }
        assert result == expectation

        result = read_number_available_for_item(connection, "Inaccessible Drill Rig")
        expectation = {
            "Big Ben": 1,
            "Antarctica Ace": 0,
            "Alaska Station": 0,
            "Hawaii Depo": 0,
        }
        assert result == expectation

        result = read_number_available_for_item(connection, "Extreme Weather Drysuit")
        expectation = {
            "Big Ben": 0,
            "Antarctica Ace": 1,
            "Alaska Station": 0,
            "Hawaii Depo": 0,
        }
        assert result == expectation

        result = read_number_available_for_item(connection, "Quantum Core Switch")
        expectation = {
            "Big Ben": 3,
            "Antarctica Ace": 0,
            "Alaska Station": 1,
            "Hawaii Depo": 0,
        }
        assert result == expectation

    finally:
        connection.close()


def test_readSoldoutUnorderedItems():
    """Tests the read_soldout_unordered_items function"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_soldout_unordered_items(connection, "Invalid Name")
        expectation = None
        assert result == expectation

        result = read_soldout_unordered_items(connection, "Secret Vault")
        expectation = None
        assert result == expectation

        result = read_soldout_unordered_items(connection, "Hawaii Depo")
        expectation = []
        assert result == expectation

        result = read_soldout_unordered_items(connection, "Alaska Station")
        expectation = [
            ["Blown Fuse Box", datetime.datetime(2026, 9, 24, 11, 30, 25)],
            ["Corrupted GPS Unit", datetime.datetime(2026, 9, 16, 11, 30, 25)],
            ["Cracked Snow Goggles", datetime.datetime(2026, 9, 19, 11, 30, 25)],
            ["Defective Arctic Tent", datetime.datetime(2026, 9, 12, 11, 30, 25)],
            ["Flooded VHF Radio", datetime.datetime(2026, 9, 22, 11, 30, 25)],
            ["Inaccessible Drill Rig", datetime.datetime(2026, 9, 9, 11, 30, 25)],
            ["Locked Safety Vault", datetime.datetime(2026, 9, 14, 11, 30, 25)],
        ]
        assert result == expectation

        result = read_soldout_unordered_items(connection, "Big Ben")
        expectation = [
            ["Corrupted Storage Array", datetime.datetime(2026, 8, 14, 11, 30, 25)]
        ]
        assert result == expectation

        result = read_soldout_unordered_items(connection, "Antarctica Ace")
        expectation = []
        assert result == expectation

    finally:
        connection.close()


def test_readSupplierCountAvailableItems():
    """Tests the read_supplier_count_of_available_item function"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_supplier_count_of_available_item(connection, "Invalid Name")
        expectation = {
            "Alaska Station": ["None"],
            "Antarctica Ace": ["None"],
            "Hawaii Depo": ["None"],
            "Big Ben": ["None"],
        }
        assert result == expectation

        result = read_supplier_count_of_available_item(
            connection, "Inaccessible Drill Rig"
        )
        expectation = {
            "Alaska Station": ["None"],
            "Antarctica Ace": ["None"],
            "Hawaii Depo": ["None"],
            "Big Ben": ["Titanium Industrial Foundry"],
        }
        assert result == expectation

        result = read_supplier_count_of_available_item(
            connection, "Extreme Weather Drysuit"
        )
        expectation = {
            "Alaska Station": ["None"],
            "Antarctica Ace": ["Quantum Tech Components"],
            "Hawaii Depo": ["None"],
            "Big Ben": ["None"],
        }
        assert result == expectation

        result = read_supplier_count_of_available_item(
            connection, "Quantum Core Switch"
        )
        expectation = {
            "Alaska Station": ["Quantum Tech Components"],
            "Antarctica Ace": ["None"],
            "Hawaii Depo": ["None"],
            "Big Ben": [
                "Quantum Tech Components",
                "Quantum Tech Components",
                "Titanium Industrial Foundry",
            ],
        }
        assert result == expectation

    finally:
        connection.close()


def test_readItemsStatsGivenName():
    """Tests the read_item_stats_given_name_and_warehouse function"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_item_stats_given_name_and_warehouse(
            connection, "Invalid Name", "Invalid Name"
        )
        expectation = None
        assert result == expectation

        result = read_item_stats_given_name_and_warehouse(
            connection, "Inaccessible Drill Rig", "Invalid Name"
        )
        expectation = None

        result = read_item_stats_given_name_and_warehouse(
            connection, "Invalid Name", "Big Ben"
        )
        expectation = []

        result = read_item_stats_given_name_and_warehouse(
            connection, "Quantum Core Switch", "Big Ben"
        )
        expectation = [
            [Decimal("8400.000"), "Quantum Tech Components", "SN-BB-205", 12],
            [Decimal("8410.000"), "Quantum Tech Components", "SN-BB-206", 13],
            [Decimal("8420.000"), "Titanium Industrial Foundry", "SN-BB-207", 14],
        ]
        assert result == expectation

    finally:
        connection.close()


def test_readItemsStatsGivenCategory():
    """Tests the read_item_stats_given_category_and_warehouse function"""
    connection = connect_and_init_safely("Data/inventory_testing.sql")
    try:
        result = read_item_stats_given_category_and_warehouse(
            connection, "Invalid Name", "Invalid Name"
        )
        expectation = None
        assert result == expectation

        result = read_item_stats_given_category_and_warehouse(
            connection, "Electronics", "Invalid Name"
        )
        expectation = None

        result = read_item_stats_given_category_and_warehouse(
            connection, "Invalid Name", "Big Ben"
        )
        expectation = []

        result = read_item_stats_given_category_and_warehouse(
            connection, "Electronics", "Shadow Depot"
        )
        expectation = []

        result = read_item_stats_given_category_and_warehouse(
            connection, "Electronics", "Big Ben"
        )
        expectation = [
            [
                "Quantum Core Switch",
                Decimal("8400.000"),
                "Quantum Tech Components",
                "SN-BB-205",
                12,
            ],
            [
                "Quantum Core Switch",
                Decimal("8410.000"),
                "Quantum Tech Components",
                "SN-BB-206",
                13,
            ],
            [
                "Quantum Core Switch",
                Decimal("8420.000"),
                "Titanium Industrial Foundry",
                "SN-BB-207",
                14,
            ],
            [
                "Smart Logistics Scanners",
                Decimal("620.000"),
                "Global Optic Logistics",
                "SN-BB-214",
                21,
            ],
            [
                "Smart Logistics Scanners",
                Decimal("630.000"),
                "Global Optic Logistics",
                "SN-BB-215",
                22,
            ],
        ]
        assert result == expectation

    finally:
        connection.close()
