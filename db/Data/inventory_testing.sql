
--- SEED DATA ---
-------------------------------------------------------------------------------

SET test.anchor_time = '2026-09-24 11:30:25';

-- WAREHOUSES
-------------------------------------------------------------------------------
INSERT INTO zipCode (zip, city, state) VALUES 
('1234 121', 'IDK', 'Hawaii'),
('1234 289', 'IDK', 'Alaska'),
('1234 357', 'London', 'None'),
('1234 401', 'IceWall', 'None'),
('1234 509', 'IDK', 'Nevada'),
('1234 619', 'Berlin', 'None');

INSERT INTO warehouse (name, street, zip, is_public) VALUES 
('Hawaii Depo', 'Hawaii Highway 101', '1234 121', true),
('Alaska Station', 'Avenue Avenue 101', '1234 289', true),
('Big Ben', 'Universal UK 101', '1234 357', true),
('Antarctica Ace', 'Antarctica Avenue 101', '1234 401', true),
('Secret Vault', 'Universal USA 101', '1234 509', false),
('Shadow Depot', 'Shadow Street 101', '1234 619', false);

-------------------------------------------------------------------------------
-- ITEM CATEGORIES
-------------------------------------------------------------------------------
INSERT INTO itemCategory (name) VALUES 
('Electronics'), 
('Apparel'), 
('Heavy Machinery');

-------------------------------------------------------------------------------
-- SUPPLIERS
-------------------------------------------------------------------------------
INSERT INTO supplier (name, email) VALUES 
('Global Optic Logistics', 'orders@globaloptics.com'),
('Apex Thermal Systems', 'support@apexthermal.de'),
('Titanium Industrial Foundry', 'b2b@titanfoundry.com'),
('Quantum Tech Components', 'supply@quantumtech.io'),
('Deep Cold Outfitters', 'polar-gear@antarcticasupply.com');

-------------------------------------------------------------------------------
-- CUSTOMERS
-------------------------------------------------------------------------------
INSERT INTO customer (name, email) VALUES 
('Alpha Research Corp', 'contact@alpharesearch.org'),
('Omega Defense Systems', 'procurement@omegadef.com'),
('Euro Cargo Group', 'logistics@eurocargo.eu');

-------------------------------------------------------------------------------
-- EMPLOYEES & STAFF ROLES
-------------------------------------------------------------------------------
-- Alaska Station (Warehouse 2): 3 supervisors, 10 staff
INSERT INTO employee (employee_id, name, email, home_warehouse_id, supervisor_id, employee_type) VALUES
(1, 'Alaska Super 1', 'alsuper1@company.com', 2, NULL, 'Supervisor'),
(2, 'Alaska Super 2', 'alsuper2@company.com', 2, 1, 'Supervisor'),
(3, 'Alaska Super 3', 'alsuper3@company.com', 2, 1, 'Supervisor'),
(4, 'Alaska Staff 1', 'alstaff1@company.com', 2, 2, 'WarehouseStaff'),
(5, 'Alaska Staff 2', 'alstaff2@company.com', 2, 2, 'WarehouseStaff'),
(6, 'Alaska Staff 3', 'alstaff3@company.com', 2, 2, 'WarehouseStaff'),
(7, 'Alaska Staff 4', 'alstaff4@company.com', 2, 2, 'WarehouseStaff'),
(8, 'Alaska Staff 5', 'alstaff5@company.com', 2, 2, 'WarehouseStaff'),
(9, 'Alaska Staff 6', 'alstaff6@company.com', 2, 3, 'WarehouseStaff'),
(10, 'Alaska Staff 7', 'alstaff7@company.com', 2, 3, 'WarehouseStaff'),
(11, 'Alaska Staff 8', 'alstaff8@company.com', 2, 3, 'WarehouseStaff'),
(12, 'Alaska Staff 9', 'alstaff9@company.com', 2, 3, 'WarehouseStaff'),
(13, 'Alaska Staff 10', 'alstaff10@company.com', 2, 3, 'WarehouseStaff');

-- Big Ben (Warehouse 3): 1 super of 1 super of 6 staff
INSERT INTO employee (employee_id, name, email, home_warehouse_id, supervisor_id, employee_type) VALUES
(14, 'Big Ben Tier 1 Super', 'bb_s1@company.com', 3, NULL, 'Supervisor'),
(15, 'Big Ben Tier 2 Super', 'bb_s2@company.com', 3, 14, 'Supervisor'),
(16, 'Big Ben Staff 1', 'bb_st1@company.com', 3, 15, 'WarehouseStaff'),
(17, 'Big Ben Staff 2', 'bb_st2@company.com', 3, 15, 'WarehouseStaff'),
(18, 'Big Ben Staff 3', 'bb_st3@company.com', 3, 15, 'WarehouseStaff'),
(19, 'Big Ben Staff 4', 'bb_st4@company.com', 3, 15, 'WarehouseStaff'),
(20, 'Big Ben Staff 5', 'bb_st5@company.com', 3, 15, 'WarehouseStaff'),
(21, 'Big Ben Staff 6', 'bb_st6@company.com', 3, 15, 'WarehouseStaff');

-- Antarctica Ace (Warehouse 4): 5-deep supervisor chain
INSERT INTO employee (employee_id, name, email, home_warehouse_id, supervisor_id, employee_type) VALUES
(22, 'Antarctica Level 1', 'ant1@company.com', 4, NULL, 'Supervisor'),
(23, 'Antarctica Level 2', 'ant2@company.com', 4, 22, 'Supervisor'),
(24, 'Antarctica Level 3', 'ant3@company.com', 4, 23, 'Supervisor'),
(25, 'Antarctica Level 4', 'ant4@company.com', 4, 24, 'Supervisor'),
(26, 'Antarctica Level 5', 'ant5@company.com', 4, 25, 'Supervisor'),
(27, 'Antarctica End Worker', 'ant6@company.com', 4, 26, 'WarehouseStaff');

-- Promote to structural sub-tables
INSERT INTO supervisor (employee_id) VALUES (1), (2), (3), (14), (15), (22), (23), (24), (25), (26);

INSERT INTO warehouseStaff (employee_id, role_type) VALUES 
(4, 'Loader'), (5, 'Loader'), (6, 'Packer'), (7, 'Packer'), (8, 'Driver'), (9, 'Loader'), 
(10, 'Loader'), (11, 'Packer'), (12, 'Packer'), (13, 'Driver'), (16, 'Handler'), (17, 'Handler'), 
(18, 'Handler'), (19, 'Sorter'), (20, 'Sorter'), (21, 'Sorter'), (27, 'Cold-Storage Specialist');

-------------------------------------------------------------------------------
-- ITEMS (Force IDs using explicit values to ensure mapping works seamlessly)
-------------------------------------------------------------------------------
-- Hawaii Depo (1): Left empty.

-- Alaska Station (2): Discarded / Unavailable only.
INSERT INTO item (item_id, name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
(1, 'Blown Fuse Box', 'SN-AL-104', 'Discarded', 0.000, 3, 2),
(2, 'Flooded VHF Radio', 'SN-AL-105', 'Discarded', 0.000, 1, 2),
(3, 'Cracked Snow Goggles', 'SN-AL-106', 'Discarded', 0.000, 2, 2),
(4, 'Corrupted GPS Unit', 'SN-AL-107', 'Unavailable', 320.000, 1, 2),
(5, 'Locked Safety Vault', 'SN-AL-108', 'Unavailable', 1100.500, 3, 2),
(6, 'Defective Arctic Tent', 'SN-AL-109', 'Discarded', 0.000, 2, 2),
(7, 'Inaccessible Drill Rig', 'SN-AL-110', 'Unavailable', 25000.000, 3, 2),
(8, 'Inaccessible Drill Rig', 'SN-AL-111', 'Unavailable', 25100.000, 3, 2),
(9, 'Inaccessible Drill Rig', 'SN-AL-112', 'Unavailable', 25200.000, 3, 2),
(10, 'Quantum Core Switch', 'SN-AL-113', 'In Stock', 8400.000, 1, 2),
(11, 'Hydraulic Crane Arm', 'SN-AL-114', 'Delivered', 34100.000, 3, 2);

-- Big Ben (3): Mixed statuses.
INSERT INTO item (item_id, name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
(12, 'Quantum Core Switch', 'SN-BB-205', 'In Stock', 8400.000, 1, 3),
(13, 'Quantum Core Switch', 'SN-BB-206', 'In Stock', 8410.000, 1, 3),
(14, 'Quantum Core Switch', 'SN-BB-207', 'In Stock', 8420.000, 1, 3),
(15, 'Industrial Conveyor Belt', 'SN-BB-208', 'Ordered', 15400.000, 3, 3),
(16, 'Industrial Conveyor Belt', 'SN-BB-209', 'Ordered', 15400.000, 3, 3),
(17, 'High-Vis Jackets (Bulk)', 'SN-BB-210', 'In Stock', 450.000, 2, 3),
(18, 'Corrupted Storage Array', 'SN-BB-211', 'Unavailable', 1900.000, 1, 3),
(19, 'Hydraulic Crane Arm', 'SN-BB-212', 'Delivered', 34100.000, 3, 3),
(20, 'Hydraulic Crane Arm', 'SN-BB-213', 'Delivered', 34200.000, 3, 3),
(21, 'Smart Logistics Scanners', 'SN-BB-214', 'In Stock', 620.000, 1, 3),
(22, 'Smart Logistics Scanners', 'SN-BB-215', 'In Stock', 630.000, 1, 3),
(23, 'Inaccessible Drill Rig', 'SN-BB-216', 'In Stock', 25200.000, 3, 3);

-- Antarctica Ace (4): Ordered / Delivered only.
INSERT INTO item (item_id, name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
(24, 'Deep-Ice Drill Bit', 'SN-AN-303', 'Ordered', 1250.000, 3, 4),
(25, 'Deep-Ice Drill Bit', 'SN-AN-304', 'Discarded', 1350.000, 3, 4),
(26, 'Satellite Comms Dish', 'SN-AN-305', 'Delivered', 18900.000, 1, 4),
(27, 'Extreme Weather Drysuit', 'SN-AN-306', 'Delivered', 720.000, 2, 4),
(28, 'Extreme Weather Drysuit', 'SN-AN-307', 'Ordered', 721.000, 2, 4),
(29, 'Extreme Weather Drysuit', 'SN-AN-308', 'In Stock', 720.000, 2, 4);

-- Secret Vault (5): Private
INSERT INTO item (item_id, name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
(30, 'Military-Grade Encryption Key', 'SN-SV-401', 'In Stock', 55000.000, 1, 5),
(31, 'Prototype Drone Framework', 'SN-SV-402', 'Ordered', 120000.000, 3, 5),
(32, 'Extreme Weather Drysuit', 'SN-SV-403', 'In Stock', 720.000, 2, 5);

-- Shadow Depot (6): Private
INSERT INTO item (item_id, name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
(33, 'Fiber Optic Transceiver', 'SN-SD-501', 'In Stock', 120.000, 1, 6),
(34, 'Mainframe Cooling Component', 'SN-SD-504', 'Ordered', 1650.000, 1, 6),
(35, 'Thermal Imaging Monocular', 'SN-SD-506', 'Unavailable', 2900.000, 1, 6),
(36, 'Inaccessible Drill Rig', 'SN-SD-509', 'Unavailable', 25200.000, 3, 6),
(37, 'Extreme Weather Drysuit', 'SN-SD-510', 'In Stock', 720.000, 2, 6);

-------------------------------------------------------------------------------
-- SUPPLY
-------------------------------------------------------------------------------
INSERT INTO supply (item_id, supplier_id, purchase_cost, date_supplied) VALUES 
-- Alaska Station (Items 1-11)
(1, 3, 0.000, current_setting('test.anchor_time')::timestamp - INTERVAL '0 days'),   -- Blown Fuse Box
(2, 1, 0.000, current_setting('test.anchor_time')::timestamp - INTERVAL '2 days'),   -- Flooded VHF Radio
(3, 5, 0.000, current_setting('test.anchor_time')::timestamp - INTERVAL '5 days'),   -- Cracked Snow Goggles
(4, 4, 250.000, current_setting('test.anchor_time')::timestamp - INTERVAL '8 days'),  -- Corrupted GPS Unit
(5, 3, 900.000, current_setting('test.anchor_time')::timestamp - INTERVAL '10 days'), -- Locked Safety Vault
(6, 5, 0.000, current_setting('test.anchor_time')::timestamp - INTERVAL '12 days'),  -- Defective Arctic Tent
(7, 3, 20000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '15 days'),-- Inaccessible Drill Rig
(8, 3, 20100.000, current_setting('test.anchor_time')::timestamp - INTERVAL '16 days'),-- Inaccessible Drill Rig
(9, 3, 20200.000, current_setting('test.anchor_time')::timestamp - INTERVAL '18 days'),-- Inaccessible Drill Rig
(10, 4, 7000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '22 days'),-- Quantum Core Switch
(11, 3, 28000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '24 days'),-- Hydraulic Crane Arm

-- Big Ben (Items 12-23)
(12, 4, 7000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '31 days'),-- Quantum Core Switch
(13, 4, 7010.000, current_setting('test.anchor_time')::timestamp - INTERVAL '31 days'),-- Quantum Core Switch
(14, 3, 7020.000, current_setting('test.anchor_time')::timestamp - INTERVAL '31 days'),-- Quantum Core Switch
(15, 3, 12000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '36 days'),-- Industrial Conveyor Belt
(16, 3, 12000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '36 days'),-- Industrial Conveyor Belt
(17, 2, 350.000, current_setting('test.anchor_time')::timestamp - INTERVAL '39 days'), -- High-Vis Jackets (Bulk)
(18, 1, 1500.000, current_setting('test.anchor_time')::timestamp - INTERVAL '41 days'), -- Corrupted Storage Array
(19, 3, 28000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '43 days'),-- Hydraulic Crane Arm
(20, 3, 28100.000, current_setting('test.anchor_time')::timestamp - INTERVAL '43 days'),-- Hydraulic Crane Arm
(21, 1, 500.000, current_setting('test.anchor_time')::timestamp - INTERVAL '46 days'),  -- Smart Logistics Scanners
(22, 1, 510.000, current_setting('test.anchor_time')::timestamp - INTERVAL '46 days'),  -- Smart Logistics Scanners
(23, 3, 20200.000, current_setting('test.anchor_time')::timestamp - INTERVAL '49 days'),-- Inaccessible Drill Rig

-- Antarctica Ace (Items 24-28)
(24, 3, 1000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '51 days'), -- Deep-Ice Drill Bit
(25, 1, 15000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '54 days'),-- Satellite Comms Dish
(26, 5, 550.000, current_setting('test.anchor_time')::timestamp - INTERVAL '57 days'),  -- Extreme Weather Drysuit
(27, 5, 555.000, current_setting('test.anchor_time')::timestamp - INTERVAL '57 days'),  -- Extreme Weather Drysuit
(28, 5, 550.000, current_setting('test.anchor_time')::timestamp - INTERVAL '59 days'),  -- Extreme Weather Drysuit

-- Secret Vault (Items 29-31)
(29, 4, 45000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '61 days'),-- Military-Grade Encryption Key
(30, 3, 95000.000, current_setting('test.anchor_time')::timestamp - INTERVAL '64 days'),-- Prototype Drone Framework
(31, 5, 550.000, current_setting('test.anchor_time')::timestamp - INTERVAL '67 days'),  -- Extreme Weather Drysuit

-- Shadow Depot (Items 32-36)
(32, 1, 90.000, current_setting('test.anchor_time')::timestamp - INTERVAL '69 days'),   -- Fiber Optic Transceiver
(33, 2, 1300.000, current_setting('test.anchor_time')::timestamp - INTERVAL '71 days'), -- Mainframe Cooling Component
(34, 2, 2200.000, current_setting('test.anchor_time')::timestamp - INTERVAL '74 days'), -- Thermal Imaging Monocular
(35, 3, 20200.000, current_setting('test.anchor_time')::timestamp - INTERVAL '77 days'),-- Inaccessible Drill Rig
(36, 5, 550.000, current_setting('test.anchor_time')::timestamp - INTERVAL '79 days');
-------------------------------------------------------------------------------
-- CUSTOMER TRANSACTIONS & RETURNS
-------------------------------------------------------------------------------
INSERT INTO customerTransaction (transaction_id, transaction_type, transaction_date, item_id, customer_id) VALUES 
(1, 'Sale', current_setting('test.anchor_time')::timestamp - INTERVAL '5 days', 12, 1),
(2, 'Sale', current_setting('test.anchor_time')::timestamp - INTERVAL '4 days', 15, 2);

INSERT INTO itemReturn (return_date, return_condition, transaction_id) VALUES 
(current_setting('test.anchor_time')::timestamp - INTERVAL '2 days', 'Damaged Packaging', 2);

-------------------------------------------------------------------------------
-- STATUS CHANGES (Audit Logs)
-------------------------------------------------------------------------------
INSERT INTO statusChange (old_status, new_status, changed_at, item_id, employee_id) VALUES 
('Non-Existant', 'Ordered', current_setting('test.anchor_time')::timestamp - INTERVAL '30 days', 8, 16),
('Ordered', 'In Stock', current_setting('test.anchor_time')::timestamp - INTERVAL '28 days', 8, 16),
('Non-Existant', 'Ordered', current_setting('test.anchor_time')::timestamp - INTERVAL '20 days', 11, 17),
('Ordered', 'In Stock', current_setting('test.anchor_time')::timestamp - INTERVAL '18 days', 11, 17),
('In Stock', 'Unavailable', current_setting('test.anchor_time')::timestamp - INTERVAL '17 days', 11, 18),
('Non-Existant', 'Ordered', current_setting('test.anchor_time')::timestamp - INTERVAL '15 days', 12, 16),
('Ordered', 'In Stock', current_setting('test.anchor_time')::timestamp - INTERVAL '12 days', 12, 19),
('In Stock', 'Delivered', current_setting('test.anchor_time')::timestamp - INTERVAL '5 days', 12, 14),
('Non-Existant', 'Ordered', current_setting('test.anchor_time')::timestamp - INTERVAL '38 days', 15, 27),
('Ordered', 'Delivered', current_setting('test.anchor_time')::timestamp - INTERVAL '20 days', 15, 27),
('Non-Existant', 'Ordered', current_setting('test.anchor_time')::timestamp - INTERVAL '12 days', 21, 16),
('Ordered', 'In Stock', current_setting('test.anchor_time')::timestamp - INTERVAL '10 days', 21, 16),
('In Stock', 'Unavailable', current_setting('test.anchor_time')::timestamp - INTERVAL '9 days', 21, 16);
