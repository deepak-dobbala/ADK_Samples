CREATE TABLE material_order_status (
    order_id SERIAL PRIMARY KEY,
    material_name VARCHAR(100) NOT NULL,
    supplier_name VARCHAR(100) NOT NULL,
    order_date DATE NOT NULL,
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    quantity_ordered INT NOT NULL,
    quantity_received INT,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(12, 2),
    order_status VARCHAR(50) NOT NULL, -- e.g., "Ordered", "Shipped", "Delivered", "Cancelled"
    delivery_address VARCHAR(255),
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    tracking_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_check_passed BOOLEAN,  -- Indicates if the material passed quality control
    quality_check_notes TEXT,        -- Notes from the quality control check
    priority VARCHAR(20),            -- e.g., "High", "Medium", "Low"
    project_id VARCHAR(50),          -- Link to a specific project
    receiver_name VARCHAR(100),        -- Name of the person who received the delivery
    return_reason TEXT,               -- Reason for returning material if applicable
    po_number VARCHAR(50)             -- Purchase order number
);