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
CREATE TABLE IF NOT EXISTS zipCode (
    zip VARCHAR(50) NOT NULL UNIQUE PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    street VARCHAR(50) NOT NULL,
    zip VARCHAR(50) NOT NULL REFERENCES zipCode (zip) ON DELETE RESTRICT,
    is_public boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS itemCategory (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS customer (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS employee (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(255),
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    final_date TIMESTAMP DEFAULT NULL,
    home_warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE SET NULL,
    supervisor_id INT REFERENCES employee(employee_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS item (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'Ordered' NOT NULL,
    markup_price NUMERIC(10, 3) DEFAULT 0.000 NOT NULL,
    category_id INT NOT NULL REFERENCES itemCategory(category_id) ON DELETE RESTRICT,
    warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS customerTransaction (
    transaction_id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    customer_id INT NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS itemReturn (
    return_id SERIAL PRIMARY KEY,
    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    return_condition VARCHAR(50) NOT NULL,
    transaction_id INT NOT NULL REFERENCES customerTransaction(transaction_id) ON DELETE RESTRICT
);

--TODO: updates # got thtis far

CREATE TABLE IF NOT EXISTS supply (
    supply_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    supplier_id INT NOT NULL REFERENCES supplier(supplier_id) ON DELETE RESTRICT,
    purchase_cost NUMERIC(10, 3) DEFAULT 0.000 NOT NULL,
    date_supplied TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS statusChange (
    status_change_id SERIAL PRIMARY KEY,
    old_status VARCHAR(50) DEFAULT 'Ordered' NOT NULL,
    new_status VARCHAR(50) DEFAULT 'Ordered' NOT NULL,
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    employee_id INT NOT NULL REFERENCES employee(employee_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS warehouseTransfer (
    transfer_id SERIAL PRIMARY KEY,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    origin_warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE RESTRICT,
    destination_warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS management (
    supervisor_id INT NOT NULL REFERENCES employee(employee_id) ON DELETE CASCADE,
    warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE CASCADE,
    PRIMARY KEY (supervisor_id, warehouse_id)
);

CREATE TABLE IF NOT EXISTS inventoryManager (
    employee_id INT NOT NULL PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS warehouseStaff (
    employee_id INT NOT NULL PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS supervisor (
    employee_id INT NOT NULL PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE
);
