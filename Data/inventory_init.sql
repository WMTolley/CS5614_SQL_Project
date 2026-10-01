-- Clears Database
DROP TABLE IF EXISTS itemCategory CASCADE;
DROP TABLE IF EXISTS item CASCADE;
DROP TABLE IF EXISTS customerTransaction CASCADE;
DROP TABLE IF EXISTS customerReturn CASCADE;
DROP TABLE IF EXISTS supplier CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS supply CASCADE;
DROP TABLE IF EXISTS statusChange CASCADE;
DROP TABLE IF EXISTS warehouseTransfer CASCADE;
DROP TABLE IF EXISTS warehouse CASCADE;
DROP TABLE IF EXISTS employee CASCADE;
DROP TABLE IF EXISTS management CASCADE;
DROP TABLE IF EXISTS inventoryManager CASCADE;
DROP TABLE IF EXISTS warehouseStaff CASCADE;
DROP TABLE IF EXISTS supervisor CASCADE;


-- Code Identical to Data/inventory_run.sql
CREATE TABLE IF NOT EXISTS warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(50) NOT NULL,
    is_public boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS itemCategory (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    contact_info VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255),
    phone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS employee (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    contact_info VARCHAR(255) NOT NULL UNIQUE,
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    final_date TIMESTAMP,
    home_warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE SET NULL,
    supervisor_id INT REFERENCES employee(employee_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS item (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    serial_number VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'Ordered' NOT NULL,
    markup_price NUMERIC(10, 3) DEFAULT 0.000 NOT NULL,
    category_id INT REFERENCES itemCategory(category_id) ON DELETE SET NULL,
    warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS customerTransaction (
    transaction_id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT REFERENCES item(item_id) ON DELETE CASCADE,
    customer_id INT REFERENCES customer(customer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS customerReturn (
    return_id SERIAL PRIMARY KEY,
    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    condition VARCHAR(50) NOT NULL,
    transaction_id INT REFERENCES customerTransaction(transaction_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS supply (
    supply_id SERIAL PRIMARY KEY,
    item_id INT REFERENCES item(item_id) ON DELETE SET NULL,
    supplier_id INT REFERENCES supplier(supplier_id) ON DELETE SET NULL,
    purchase_cost NUMERIC(10, 3) DEFAULT 0.000 NOT NULL,
    date_supplied TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS statusChange (
    status_change_id SERIAL PRIMARY KEY,
    old_status VARCHAR(50) DEFAULT 'Ordered' NOT NULL,
    new_status VARCHAR(50) DEFAULT 'Ordered' NOT NULL,
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT REFERENCES item(item_id) ON DELETE CASCADE,
    employee_id INT REFERENCES employee(employee_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS warehouseTransfer (
    transfer_id SERIAL PRIMARY KEY,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT REFERENCES item(item_id) ON DELETE CASCADE,
    origin_warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE CASCADE,
    destination_warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS management (
    supervisor_id INT REFERENCES employee(employee_id) ON DELETE SET NULL,
    warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inventoryManager (
    employee_id INT PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS warehouseStaff (
    employee_id INT PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE,
    role VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS supervisor (
    employee_id INT PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE
);


--- SEED DATA ---
INSERT INTO warehouse (name, location, is_public) VALUES
('Washington DC Branch', 'White House, Washington DC', true),
('DisneyLand Storage', 'DisneyLand, Florida', true),
('SciFi Moon Base', 'Moon', false),
('Rundown Salon', 'Town, Alaska', true);

INSERT INTO itemCategory (name) VALUES
('Electronics'),
('Office Supplies'),
('Furniture'),
('Clothing');

INSERT INTO item (name, serial_number, status, markup_price, category_id, warehouse_id) VALUES
('Computer', 'DC-ELEC-99281', 'In Stock', 10.99, 1, 1),
('Office Lamp', 'DC-OFFI-99381', 'In Stock', 12.99, 2, 1),
('Office Lamp', 'DC-OFFI-99382', 'In Stock', 12.98, 2, 1),
('Stapler', 'DC-OFFI-44120', 'Ordered', 4500.00, 2, 1),
('Stapler', 'DC-OFFI-44121', 'Ordered', 4400.00, 2, 1),
('Rubber Stapler', 'DC-OFFI-45120', 'Ordered', 1500.00, 2, 1),
('Stapler', 'DC-OFFI-44121', 'Ordered', 4400.00, 2, 2),
('Wood Desk', 'DL-FURN-10023', 'Unavailable', 124.50, 3, 2),
('Office Lamp', 'DL-OFFI-99385', 'In Stock', 12.98, 2, 2),
('50ft Extension Cord', 'DL-ELEC-88371', 'In Stock', 10.30, 1, 2),
('Wood Desk', 'AT-FURN-10023', 'Unavailable', 124.50, 3, 4),
('Office Lamp', 'AT-OFFI-99385', 'In Stock', 12.98, 2, 4),
('Office Lamp', 'AT-OFFI-99386', 'Unavailable', 12.98, 2, 4),
('Office Lamp', 'AT-OFFI-99389', 'In Stock', 12.98, 2, 3),
('Wooden Chair', 'AT-OFFI-97286', 'Reserved', 12.98, 3, 4),
('Wooden Chair', 'AT-OFFI-97286', 'Reserved', 12.98, 3, 4),
('Metal Chair', 'AT-OFFI-97386', 'Unavailable', 12.98, 2, 4),
('Metal Chair', 'AT-OFFI-97387', 'Reserved', 12.98, 2, 4),
('50ft Extension Cord', 'AT-ELEC-88372', 'In Stock', 10.30, 1, 4),
('Wireless Mouse', 'DC-ELEC-99284', 'In Stock', 10.99, 1, 1);

INSERT INTO supplier (name, contact_info) VALUES
('Ali''s General Store', 'ali@vt.edu'),
('Emily''s Broad Store', 'emily@vt.edu');

INSERT INTO supply (item_id, supplier_id, purchase_cost, date_supplied) VALUES
(2, 1, 1.000, '2025-09-18 16:39:45'),
(3, 2, 1.000, '2024-09-18 16:39:45'),
(4, 1, 1.000, '2023-09-18 16:39:45'),
(5, 2, 1.000, '2022-09-18 16:39:45'),
(6, 1, 1.000, '2021-09-18 16:39:45'),
(7, 2, 1.000, '2020-09-18 16:39:45'),
(8, 1, 1.000, '2019-09-18 16:39:45'),
(9, 2, 1.000, '2018-09-18 16:39:45'),
(10, 1, 1.000, '2017-09-18 16:39:45'),
(11, 2, 1.000, '2016-09-18 16:39:45'),
(12, 1, 1.000, '2015-09-18 16:39:45'),
(13, 2, 1.000, '2014-09-18 16:39:45'),
(14, 1, 1.000, '2013-09-18 16:39:45'),
(15, 2, 1.000, '2012-09-18 16:39:45'),
(16, 1, 1.000, '2011-09-18 16:39:45'),
(17, 2, 1.000, '2010-09-18 16:39:45'),
(18, 1, 1.000, '2009-09-18 16:39:45'),
(1, 2, 1.000, '2026-09-18 16:39:45'),
(19, 2, 1.000, '2026-09-18 16:39:45'),
(20, 2, 1.000, '2026-09-18 16:39:45');





INSERT INTO employee (name, contact_info, hire_date, final_date, home_warehouse_id, supervisor_id) Values
('Ezra Jedi', 'jedi@gmail.edu', '2026-09-18 16:39:45', NULL, 1, NULL),
('Five Nazeem', 'inevitable@gmail.edu', '2025-09-18 16:39:45', NULL, 1, 1),
('Jace One', 'endingdata@gmail.edu', '2024-09-18 16:39:45', NULL, 1, 2),
('Magic Tree', 'infotree@gmail.edu', '2023-09-18 16:39:45', NULL, 1, 1);