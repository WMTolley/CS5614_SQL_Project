-- Schema for the inventory database.
-- Rebuild from scratch:  psql -f Data/schema.sql -f Data/seed.sql

-- Clears Database
DROP TABLE IF EXISTS userSession CASCADE;
DROP TABLE IF EXISTS userAccount CASCADE;
DROP TABLE IF EXISTS zipCode CASCADE;
DROP TABLE IF EXISTS warehouse CASCADE;
DROP TABLE IF EXISTS itemCategory CASCADE;
DROP TABLE IF EXISTS supplier CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS employee CASCADE;
DROP TABLE IF EXISTS item CASCADE;
DROP TABLE IF EXISTS customerTransaction CASCADE;
DROP TABLE IF EXISTS itemReturn CASCADE;
DROP TABLE IF EXISTS supply CASCADE;
DROP TABLE IF EXISTS statusChange CASCADE;
DROP TABLE IF EXISTS warehouseTransfer CASCADE;
DROP TABLE IF EXISTS management CASCADE;
DROP TABLE IF EXISTS inventoryManager CASCADE;
DROP TABLE IF EXISTS warehouseStaff CASCADE;
DROP TABLE IF EXISTS supervisor CASCADE;


CREATE TABLE IF NOT EXISTS zipCode (
    zip VARCHAR(10) PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_public BOOLEAN NOT NULL,
    street VARCHAR(100) NOT NULL,
    zip VARCHAR(10) NOT NULL REFERENCES zipCode (zip) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS itemCategory (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) CONSTRAINT supplier_email_format CHECK (email LIKE '_%@_%'),
    phone VARCHAR(20),
    -- A supplier must be reachable somehow
    CONSTRAINT supplier_has_contact CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS customer (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) CONSTRAINT customer_email_format CHECK (email LIKE '_%@_%'),
    phone VARCHAR(20),
    -- A customer must be reachable somehow
    CONSTRAINT customer_has_contact CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

-- Supertype of warehouseStaff, supervisor and inventoryManager (discriminator: employee_type)
CREATE TABLE IF NOT EXISTS employee (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) CONSTRAINT employee_email_format CHECK (email LIKE '_%@_%'),
    phone VARCHAR(20),
    hire_date DATE DEFAULT CURRENT_DATE NOT NULL,
    final_date DATE DEFAULT NULL,
    employee_type VARCHAR(20) NOT NULL
        CONSTRAINT employee_type_valid
        CHECK (employee_type IN ('WarehouseStaff', 'Supervisor', 'InventoryManager')),
    home_warehouse_id INT REFERENCES warehouse(warehouse_id) ON DELETE SET NULL,
    supervisor_id INT REFERENCES employee(employee_id) ON DELETE SET NULL,
    -- An employee must be reachable somehow
    CONSTRAINT employee_has_contact CHECK (email IS NOT NULL OR phone IS NOT NULL),
    -- An employee can't leave before they were hired
    CONSTRAINT employee_dates_in_order CHECK (final_date IS NULL OR final_date >= hire_date),
    -- An employee can't supervise themselves
    CONSTRAINT employee_not_own_supervisor CHECK (supervisor_id <> employee_id)
);

-- Item lifecycle: Ordered -> Delivered -> In Stock -> Reserved/Unavailable/Discarded
CREATE TABLE IF NOT EXISTS item (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'Ordered' NOT NULL
        CONSTRAINT item_status_valid
        CHECK (status IN ('Ordered', 'Delivered', 'In Stock', 'Reserved', 'Unavailable', 'Discarded')),
    markup_price DECIMAL(10, 2) DEFAULT 0.00 NOT NULL
        CONSTRAINT item_markup_price_nonnegative CHECK (markup_price >= 0),
    category_id INT NOT NULL REFERENCES itemCategory(category_id) ON DELETE RESTRICT,
    warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS customerTransaction (
    transaction_id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL
        CONSTRAINT transaction_type_valid CHECK (transaction_type IN ('Sale', 'Reservation')),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    customer_id INT NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS itemReturn (
    return_id SERIAL PRIMARY KEY,
    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    return_condition VARCHAR(30) NOT NULL,
    transaction_id INT NOT NULL REFERENCES customerTransaction(transaction_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS supply (
    supply_id SERIAL PRIMARY KEY,
    purchase_cost DECIMAL(10, 2) DEFAULT 0.00 NOT NULL
        CONSTRAINT supply_purchase_cost_nonnegative CHECK (purchase_cost >= 0),
    date_supplied DATE DEFAULT CURRENT_DATE NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    supplier_id INT NOT NULL REFERENCES supplier(supplier_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS statusChange (
    status_change_id SERIAL PRIMARY KEY,
    old_status VARCHAR(20) NOT NULL
        CONSTRAINT status_change_old_status_valid
        CHECK (old_status IN ('Non-Existant', 'Ordered', 'Delivered', 'In Stock', 'Reserved', 'Unavailable', 'Discarded')),
    new_status VARCHAR(20) NOT NULL
        CONSTRAINT status_change_new_status_valid
        CHECK (new_status IN ('Non-Existant', 'Ordered', 'Delivered', 'In Stock', 'Reserved', 'Unavailable', 'Discarded')),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    employee_id INT NOT NULL REFERENCES employee(employee_id) ON DELETE RESTRICT,
    -- A status change must actually change the status
    CONSTRAINT status_change_is_a_change CHECK (old_status <> new_status)
);

CREATE TABLE IF NOT EXISTS warehouseTransfer (
    transfer_id SERIAL PRIMARY KEY,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    item_id INT NOT NULL REFERENCES item(item_id) ON DELETE RESTRICT,
    origin_warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE RESTRICT,
    destination_warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE RESTRICT,
    -- A transfer must move the item to a different warehouse
    CONSTRAINT transfer_between_different_warehouses
        CHECK (origin_warehouse_id <> destination_warehouse_id)
);

-- Employee subtypes
CREATE TABLE IF NOT EXISTS warehouseStaff (
    employee_id INT NOT NULL PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE,
    role_type VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS supervisor (
    employee_id INT NOT NULL PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inventoryManager (
    employee_id INT NOT NULL PRIMARY KEY REFERENCES employee(employee_id) ON DELETE CASCADE
);

-- Which inventory managers manage which warehouses (M:N)
CREATE TABLE IF NOT EXISTS management (
    employee_id INT NOT NULL REFERENCES inventoryManager(employee_id) ON DELETE CASCADE,
    warehouse_id INT NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE CASCADE,
    PRIMARY KEY (employee_id, warehouse_id)
);

-- Login credentials. An account is either the admin (no profile) or linked to exactly one
-- customer or employee. An employee's permissions come from employee.employee_type.
CREATE TABLE IF NOT EXISTS userAccount (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    customer_id INT UNIQUE REFERENCES customer(customer_id) ON DELETE CASCADE,
    employee_id INT UNIQUE REFERENCES employee(employee_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Admins have no profile; everyone else is exactly one of customer or employee
    CONSTRAINT account_profile_valid CHECK (
        (is_admin AND customer_id IS NULL AND employee_id IS NULL)
        OR (NOT is_admin AND num_nonnulls(customer_id, employee_id) = 1)
    )
);

-- Usernames are case-insensitive
CREATE UNIQUE INDEX IF NOT EXISTS userAccount_username_lower
    ON userAccount (lower(username));

-- Server-side login sessions; only a hash of the token is stored. Logout deletes the row.
CREATE TABLE IF NOT EXISTS userSession (
    token_hash VARCHAR(64) PRIMARY KEY,
    user_id INT NOT NULL REFERENCES userAccount(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    CONSTRAINT session_expires_after_created CHECK (expires_at > created_at)
);
