from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.templating import Jinja2Templates

from backend.src.utils.db import setup_database
from backend.src.utils.scemas import Cart, Orders, Products

app = FastAPI()
templates = Jinja2Templates(directory="frontend/src/templates")

db = setup_database(app)


@app.get("/health")
async def health_check(conn=Depends(db.connection)):
    await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected"}


@app.post("/api/products")
async def post_products(products: Products, conn=Depends(db.connection)):
    sql = "INSERT INTO products (product_name, price, quantity, description, product_picture) VALUES ($1, $2, $3, $4, $5)"
    result = await conn.execute(
        sql,
        products.product_name,
        products.price,
        products.quantity,
        products.description,
        products.product_picture,
    )

    return {"msg": "berhasil upload", "data": result}


@app.put("/api/products/{id}")
async def update_products(id: int, products: Products, conn=Depends(db.connection)):
    sql = """
    UPDATE products
    SET product_name = $1,
        price = $2,
        quantity = $3,
        description = $4,
        product_picture = $5
    WHERE id = $6
    """

    result = await conn.execute(
        sql,
        id,
        products.product_name,
        products.price,
        products.quantity,
        products.description,
        products.product_picture,
    )

    return {"msg": "berhasil update", "data": result}


@app.get("/api/products")
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    conn=Depends(db.connection),
):
    offset = (page - 1) * limit

    sql = """
        SELECT id, product_name, price, quantity, description, product_picture
        FROM products
        ORDER BY id ASC
        LIMIT $1 OFFSET $2
    """

    rows = await conn.fetch(sql, limit, offset)
    total_count = await conn.fetchval("SELECT COUNT(*) FROM products")
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    products_list = [dict(row) for row in rows]

    return {
        "page": page,
        "limit": limit,
        "total_items": len(products_list),
        "total_pages": total_pages,
        "data": products_list,
    }


@app.delete("/api/products/{id}")
async def delete_products(id: int, conn=Depends(db.connection)):
    sql = "DELETE FROM products WHERE id = $1"
    result = await conn.execute(sql, id)
    return {"msg": "berhasil delete", "data": result}


@app.get("/api/cart")
async def get_cart(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    conn=Depends(db.connection),
):
    sql = """
        SELECT id, product_name, price, product_picture, quantity, user_id, product_id
        FROM cart
        ORDER BY id ASC
        LIMIT $1 OFFSET $2
    """

    offset = (page - 1) * limit

    rows = await conn.fetch(sql, limit, offset)
    total_count = await conn.fetchval("SELECT COUNT(*) FROM products")
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    products_list = [dict(row) for row in rows]

    return {
        "page": page,
        "limit": limit,
        "total_items": len(products_list),
        "total_pages": total_pages,
        "data": products_list,
    }


@app.post("/api/cart")
async def add_cart(cart: Cart, conn=Depends(db.connection)):
    sql = "INSERT INTO cart (id, product_name, price, product_picture, product_picture, quantity, user_id, product_id) VALUES ($1, $2, $3, $4, $5, $6, $7)"
    result = await conn.execute(
        sql,
        cart.id,
        cart.product_name,
        cart.price,
        cart.product_picture,
        cart.quantity,
        cart.user_id,
        cart.product_id,
    )

    return {"msg": "success", "data": result}


@app.delete("/api/cart/{id}")
async def delete_cart(id: int, conn=Depends(db.connection)):
    sql = "DELETE FROM products WHERE id = $1"
    result = await conn.execute(sql, id)
    return {"msg": "berhasil delete", "data": result}


@app.post("/api/order")
async def order_items(order: Orders, conn=Depends(db.connection)):
    async with conn.transaction():
        product = await conn.fetchrow(
            "SELECT id, product_name, price, quantity, product_picture FROM products WHERE id = $1 FOR UPDATE",
            order.id,
        )

        if not product:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

        if product["quantity"] < order.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stok tidak cukup! Tersisa: {product['quantity']}",
            )

        total_price = float(product["price"]) * order.quantity

        await conn.execute(
            "UPDATE products SET quantity = quantity - $1 WHERE id = $2",
            order.quantity,
            order.id,
        )

        current_user_id = 1

        insert_sql = """
            INSERT INTO orders (
                product_name,
                price,
                quantity,
                recipient_name,
                recipient_address,
                total_price,
                product_picture,
                user_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *;
        """

        new_order = await conn.fetchrow(
            insert_sql,
            product["product_name"],
            product["price"],
            order.quantity,
            order.recipient_name,
            order.recipient_address,
            total_price,
            product["product_picture"],
            current_user_id,
        )

    return new_order


@app.get("/api/orders/history", response_model=list[Orders])
async def get_order_history(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    conn=Depends(db.connection),
):
    sql = """
        SELECT * FROM orders
        WHERE user_id = $1
        ORDER BY id DESC
        LIMIT $2 OFFSET $3
    """

    rows = await conn.fetch(sql, user_id, limit, offset)

    if not rows:
        return []

    return rows
