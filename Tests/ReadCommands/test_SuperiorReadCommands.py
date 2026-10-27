from datetime import date, datetime

from db.ReadCommands.superior_read_commands import (
    read_itemCount_given_warehouse,
    read_iteminfo_in_warehouse,
    read_statusChanges_of_employee,
    read_subordinates_of_named_employee,
)
from db.sql_commands import (
    connect_and_init,
)

# For every get function with a paramter make sure to see if its possible to test:
#    An invalid input that should return None (ie asking about items in a nonexistant warehouse)
#    An input that requires other permission should return None (ie asking about items in a private warehouse)
#    An input that should return nothing / [] (ie asking about items in a warehouse thats empty)
#    A valid input


def test_read_subordinates_of_named_employee():
    """Tests that read_subordinates_of_named_employee correctly returns the correct employees"""
    connection = connect_and_init("db/Data/schema.sql", "db/Data/inventory_testing.sql")
    try:
        result = read_subordinates_of_named_employee(connection, "NonExistant")
        expectation = None
        assert result == expectation

        result = read_subordinates_of_named_employee(connection, "Alaska Staff 10")
        expectation = []
        assert result == expectation

        result = read_subordinates_of_named_employee(connection, "Alaska Super 1")
        expectation = [
            "Alaska Super 2",
            "Alaska Super 3",
        ]
        assert result == expectation

        result = read_subordinates_of_named_employee(connection, "Alaska Super 2")
        expectation = [
            "Alaska Staff 1",
            "Alaska Staff 2",
            "Alaska Staff 3",
            "Alaska Staff 4",
            "Alaska Staff 5",
        ]
        assert result == expectation

        result = read_subordinates_of_named_employee(connection, "Antarctica Level 3")
        expectation = [
            "Antarctica Level 4",
        ]
        assert result == expectation
    finally:
        connection.close()


def test_read_statusChanges_of_employee():
    """Tests that read_statusChanges_of_employee correctly returns the correct status change entries"""
    connection = connect_and_init("db/Data/schema.sql", "db/Data/inventory_testing.sql")
    try:
        result = read_statusChanges_of_employee(connection, "NonExistant")
        expectation = None
        assert result == expectation

        result = read_statusChanges_of_employee(connection, "Alaska Staff 10")
        expectation = []
        assert result == expectation

        result = read_statusChanges_of_employee(connection, "Big Ben Staff 1")
        expectation = [
            [
                "Non-Existant",
                "Ordered",
                8,
                datetime(2026, 8, 25, 11, 30, 25),
            ],
            [
                "Ordered",
                "In Stock",
                8,
                datetime(2026, 8, 27, 11, 30, 25),
            ],
            [
                "Non-Existant",
                "Ordered",
                12,
                datetime(2026, 9, 9, 11, 30, 25),
            ],
            [
                "Non-Existant",
                "Ordered",
                21,
                datetime(2026, 9, 12, 11, 30, 25),
            ],
            [
                "Ordered",
                "In Stock",
                21,
                datetime(2026, 9, 14, 11, 30, 25),
            ],
            [
                "In Stock",
                "Unavailable",
                21,
                datetime(2026, 9, 15, 11, 30, 25),
            ],
        ]
        assert result == expectation

        result = read_statusChanges_of_employee(connection, "Big Ben Staff 3")
        expectation = [
            [
                "In Stock",
                "Unavailable",
                11,
                datetime(2026, 9, 7, 11, 30, 25),
            ],
        ]
        assert result == expectation
    finally:
        connection.close()


def test_read_itemCount_given_warehouse():
    """Tests read_itemCount_given_warehouse"""
    connection = connect_and_init("db/Data/schema.sql", "db/Data/inventory_testing.sql")
    try:
        result = read_itemCount_given_warehouse(connection, warehouse_id=50)
        expectation = []
        assert result == expectation

        result = read_itemCount_given_warehouse(connection, warehouse_name="Invalid")
        expectation = []
        assert result == expectation

        result = read_itemCount_given_warehouse(
            connection, warehouse_name="Invalid", warehouse_id=50
        )
        expectation = []
        assert result == expectation

        result = read_itemCount_given_warehouse(connection)
        expectation = None
        assert result == expectation

        result = read_itemCount_given_warehouse(connection, warehouse_id=1)
        expectation = []
        assert result == expectation

        result = read_itemCount_given_warehouse(connection, warehouse_id=2)
        expectation = [
            ["Blown Fuse Box", 0, date(2026, 9, 24)],
            ["Flooded VHF Radio", 0, date(2026, 9, 22)],
            ["Cracked Snow Goggles", 0, date(2026, 9, 19)],
            ["Corrupted GPS Unit", 0, date(2026, 9, 16)],
            ["Locked Safety Vault", 0, date(2026, 9, 14)],
            ["Defective Arctic Tent", 0, date(2026, 9, 12)],
            ["Inaccessible Drill Rig", 0, date(2026, 9, 9)],
            ["Quantum Core Switch", 1, date(2026, 9, 2)],
            ["Hydraulic Crane Arm", 0, date(2026, 8, 31)],
        ]
        assert result == expectation

        result = read_itemCount_given_warehouse(connection, warehouse_id=3)
        expectation = [
            ["Quantum Core Switch", 3, date(2026, 8, 24)],
            ["Industrial Conveyor Belt", 0, date(2026, 8, 19)],
            ["High-Vis Jackets (Bulk)", 1, date(2026, 8, 16)],
            ["Corrupted Storage Array", 0, date(2026, 8, 14)],
            ["Hydraulic Crane Arm", 0, date(2026, 8, 12)],
            ["Smart Logistics Scanners", 2, date(2026, 8, 9)],
            ["Inaccessible Drill Rig", 1, date(2026, 8, 6)],
        ]
        assert result == expectation

        result = read_itemCount_given_warehouse(connection, warehouse_id=5)
        expectation = [
            ["Military-Grade Encryption Key", 1, date(2026, 7, 22)],
            ["Prototype Drone Framework", 0, date(2026, 7, 19)],
            ["Extreme Weather Drysuit", 1, date(2026, 7, 17)],
        ]
        assert result == expectation

    finally:
        connection.close()


def test_read_iteminfo_in_warehouse():
    """Tests read_iteminfo_in_warehouse"""
    connection = connect_and_init("db/Data/schema.sql", "db/Data/inventory_testing.sql")
    try:
        result = read_iteminfo_in_warehouse(connection, warehouse_id=50)
        expectation = []
        assert result == expectation

        result = read_iteminfo_in_warehouse(connection, warehouse_name="Invalid")
        expectation = []
        assert result == expectation

        result = read_iteminfo_in_warehouse(
            connection, warehouse_name="Invalid", warehouse_id=50
        )
        expectation = []
        assert result == expectation

        result = read_iteminfo_in_warehouse(connection)
        expectation = None
        assert result == expectation

        result = read_iteminfo_in_warehouse(connection, warehouse_id=1)
        expectation = []
        assert result == expectation

        result = read_iteminfo_in_warehouse(connection, warehouse_id=2)
        expectation = [
            ["Blown Fuse Box", "Discarded", "Titanium Industrial Foundry", 0.00, 0.00],
            [
                "Corrupted GPS Unit",
                "Unavailable",
                "Quantum Tech Components",
                250.00,
                320.00,
            ],
            ["Cracked Snow Goggles", "Discarded", "Deep Cold Outfitters", 0.00, 0.00],
            ["Defective Arctic Tent", "Discarded", "Deep Cold Outfitters", 0.00, 0.00],
            ["Flooded VHF Radio", "Discarded", "Global Optic Logistics", 0.00, 0.00],
            [
                "Hydraulic Crane Arm",
                "Delivered",
                "Titanium Industrial Foundry",
                28000.00,
                34100.00,
            ],
            [
                "Inaccessible Drill Rig",
                "Unavailable",
                "Titanium Industrial Foundry",
                20200.00,
                25200.00,
            ],
            [
                "Inaccessible Drill Rig",
                "Unavailable",
                "Titanium Industrial Foundry",
                20100.00,
                25100.00,
            ],
            [
                "Inaccessible Drill Rig",
                "Unavailable",
                "Titanium Industrial Foundry",
                20000.00,
                25000.00,
            ],
            [
                "Locked Safety Vault",
                "Unavailable",
                "Titanium Industrial Foundry",
                900.00,
                1100.50,
            ],
            [
                "Quantum Core Switch",
                "In Stock",
                "Quantum Tech Components",
                7000.00,
                8400.00,
            ],
        ]
        assert result == expectation

        result = read_iteminfo_in_warehouse(connection, warehouse_id=3)
        expectation = [
            [
                "Corrupted Storage Array",
                "Unavailable",
                "Global Optic Logistics",
                1500.00,
                1900.00,
            ],
            [
                "High-Vis Jackets (Bulk)",
                "In Stock",
                "Apex Thermal Systems",
                350.00,
                450.00,
            ],
            [
                "Hydraulic Crane Arm",
                "Delivered",
                "Titanium Industrial Foundry",
                28100.00,
                34200.00,
            ],
            [
                "Hydraulic Crane Arm",
                "Delivered",
                "Titanium Industrial Foundry",
                28000.00,
                34100.00,
            ],
            [
                "Inaccessible Drill Rig",
                "In Stock",
                "Titanium Industrial Foundry",
                20200.00,
                25200.00,
            ],
            [
                "Industrial Conveyor Belt",
                "Ordered",
                "Titanium Industrial Foundry",
                12000.00,
                15400.00,
            ],
            [
                "Industrial Conveyor Belt",
                "Ordered",
                "Titanium Industrial Foundry",
                12000.00,
                15400.00,
            ],
            [
                "Quantum Core Switch",
                "In Stock",
                "Quantum Tech Components",
                7010.00,
                8410.00,
            ],
            [
                "Quantum Core Switch",
                "In Stock",
                "Titanium Industrial Foundry",
                7020.00,
                8420.00,
            ],
            [
                "Quantum Core Switch",
                "In Stock",
                "Quantum Tech Components",
                7000.00,
                8400.00,
            ],
            [
                "Smart Logistics Scanners",
                "In Stock",
                "Global Optic Logistics",
                510.00,
                630.00,
            ],
            [
                "Smart Logistics Scanners",
                "In Stock",
                "Global Optic Logistics",
                500.00,
                620.00,
            ],
        ]
        assert result == expectation

        result = read_iteminfo_in_warehouse(connection, warehouse_id=5)
        expectation = [
            [
                "Extreme Weather Drysuit",
                "In Stock",
                "Global Optic Logistics",
                90.00,
                720.00,
            ],
            [
                "Military-Grade Encryption Key",
                "In Stock",
                "Titanium Industrial Foundry",
                95000.00,
                55000.00,
            ],
            [
                "Prototype Drone Framework",
                "Ordered",
                "Deep Cold Outfitters",
                550.00,
                120000.00,
            ],
        ]
        assert result == expectation

    finally:
        connection.close()
