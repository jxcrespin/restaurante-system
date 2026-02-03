DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS tables;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('WAITER', 'KITCHEN', 'CASHIER') NOT NULL
);

CREATE TABLE tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    number INT NOT NULL
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_id INT NULL,
    order_type ENUM('TABLE', 'TAKEAWAY') NOT NULL,
    status ENUM('CREATED', 'COOKING', 'READY', 'DELIVERED', 'PAID') DEFAULT 'CREATED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price_snapshot DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO tables (number) VALUES
(1),(2),(3),(4),(5),(6),(7),(8);

INSERT INTO categories (name) VALUES
('Platos'),('Caldos'),('Chuzos'),('Bebidas');

INSERT INTO products (name, price, category_id) VALUES
('Caldo de Gallina', 8.00, 2),
('Caldo de Pata', 8.00, 2),
('Camarones Apanados', 8.00, 1),
('Corvina Frita', 8.00, 1),
('Estofado de Carne', 8.00, 1),
('Encocado de Camarones', 8.00, 1),
('Filete de Pescado', 8.00, 1),
('Guatita', 8.00, 1),
('Seco de Chancho', 8.00, 1),
('Seco de Chivo', 8.00, 1),
('Seco de Costilla', 5.00, 1),
('Seco de Gallina', 8.00, 1),
('Seco de Pollo', 1.50, 1),
('Chuzo de Pollo', 1.50, 3),
('Chuzo de Carne', 1.50, 3),
('Jugo Personal', 0.50, 4),
('Cola Personal', 0.50, 4),
('Cola 1 Litro', 1.25, 4),
('Fusetea', 1.50, 4);

INSERT INTO users (username, password, role) VALUES
('mesero1', '1234', 'WAITER'),
('cocina1', '1234', 'KITCHEN'),
('caja1', '1234', 'CASHIER');

-- mejoras 
ALTER TABLE tables ADD COLUMN status ENUM('FREE','OCCUPIED') DEFAULT 'FREE';

UPDATE tables SET status='FREE';

CREATE TABLE order_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    table_id INT,
    occupied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    freed_at TIMESTAMP NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (table_id) REFERENCES tables(id)
);
