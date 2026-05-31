CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
<<<<<<< HEAD
    phone_number VARCHAR(20) NOT NULL, 
    email VARCHAR(100) NOT NULL UNIQUE, 
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
=======
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    address TEXT
>>>>>>> 3fe070cb4d321a56b6fa04e374161ddb5bf0094c
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    description VARCHAR(200) NOT NULL,
    product_picture VARCHAR(100) NOT NULL,
    user_id BIGINT,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
<<<<<<< HEAD

    product_id INT,
    product_name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    quantity INT NOT NULL,

    recipient_name VARCHAR(100) NOT NULL,
    recipient_address TEXT NOT NULL,

    total_price NUMERIC(10,2) NOT NULL,

    product_picture VARCHAR(100),
    payment_picture TEXT,

    user_id BIGINT,

    status VARCHAR(20) DEFAULT 'pending',

    shipping_status VARCHAR(20) DEFAULT 'processing',

    patokan VARCHAR(20) NOT NULL,


    order_code VARCHAR(50) UNIQUE,

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE alamat(
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    receipient_address TEXT NOT NULL,
     FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
)
=======
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    recipient_name VARCHAR(100) NOT NULL,
    recipient_address TEXT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    product_picture VARCHAR(100) NOT NULL,
    user_id BIGINT,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
>>>>>>> 3fe070cb4d321a56b6fa04e374161ddb5bf0094c

CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    product_picture VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    user_id BIGINT,
    product_id BIGINT,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);
