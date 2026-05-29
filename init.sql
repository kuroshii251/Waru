CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,  -- Gunakan VARCHAR untuk nomor telepon
    email VARCHAR(100) NOT NULL UNIQUE, -- Tambahkan UNIQUE untuk email
    password VARCHAR(100) NOT NULL
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
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,       -- Ubah dari VARCHAR ke DECIMAL
    quantity INT NOT NULL,
    recipient_name VARCHAR(100) NOT NULL,
    recipient_address TEXT NOT NULL,    -- Gunakan TEXT untuk alamat panjang
    total_price DECIMAL(10,2) NOT NULL, -- Ubah dari VARCHAR ke DECIMAL
    product_picture VARCHAR(100) NOT NULL,
    user_id BIGINT,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,       -- Ubah dari VARCHAR ke DECIMAL
    product_picture VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    user_id BIGINT,
    product_id BIGINT,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id)
        REFERENCES products(id)         -- Pastikan nama tabel 'products' sesuai
        ON DELETE CASCADE
);
