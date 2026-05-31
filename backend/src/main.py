import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from fastapi import Depends, FastAPI, HTTPException, Query, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from backend.src.utils.db import setup_database, get_conn
from backend.src import models
from typing import Optional
import uuid
import os
from pathlib import Path
import shutil
from datetime import datetime
from backend.src.utils.scemas import (
    Products,
    Cart,
    Orders,
    Users,
    Alamat,
)
from backend.src.middleware.auth import (
    auth_middleware,
    auth_required,
    admin_required
)
from starlette.middleware.base import BaseHTTPMiddleware
import bcrypt
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
BASE_DIR = Path("/var/task")


templates = Jinja2Templates(directory=str(BASE_DIR / "frontend/src/templates"))

setup_database(app)
app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check(conn=Depends(get_conn)):
    await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected"}


@app.post("/api/auth/register")
async def register(
    request: Request,
    name: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    conn=Depends(get_conn)
):
    check_user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)

    if check_user:
        return templates.TemplateResponse(
            "auth/auth.html",
            {"request": request, "register_error": "Email sudah dipakai", "active_tab": "signup"}
        )

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await conn.execute(
        "INSERT INTO users (name, phone_number, email, password) VALUES ($1, $2, $3, $4)",
        name, phone_number, email, hashed_password
    )
    return RedirectResponse(url="/auth", status_code=303)


@app.get("/auth")
async def auth_page(request: Request):
    return templates.TemplateResponse("auth/auth.html", {"request": request})


@app.get("/add-product")
async def add_product(request: Request):
    return templates.TemplateResponse("admin/product/add_product.html", {"request": request})


@app.post("/api/auth/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    conn=Depends(get_conn)
):
    user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return templates.TemplateResponse(
            "auth/auth.html",
            {"request": request, "error": "Email atau password salah"}
        )

    request.session["user"] = {"id": user["id"], "email": user["email"], "role": user["role"]}

    if user["role"] == "admin":
        return RedirectResponse(url="/dashboard-admin", status_code=303)
    return RedirectResponse(url="/dashboard-admin", status_code=303)


@app.get("/list-users", response_class=HTMLResponse)
async def show_users(
    request: Request,
    conn=Depends(get_conn),
    user=Depends(admin_required)
):
    users = await conn.fetch("SELECT id, name, email, role FROM users ORDER BY id")
    return templates.TemplateResponse("admin/userlist.html", {"request": request, "users": users})


@app.get("/list-product", response_class=HTMLResponse)
async def show_products(
    request: Request,
    conn=Depends(get_conn),
    user=Depends(admin_required)
):
    products = await conn.fetch(
        "SELECT id, product_name, price, quantity, description, product_picture FROM products ORDER BY id"
    )
    return templates.TemplateResponse(
        "admin/product/main.html", {"request": request, "products": products}
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth")

    products = await conn.fetch(
        "SELECT id, product_name, price, quantity, description, product_picture FROM products ORDER BY id"
    )
    cart_count = await conn.fetchval(
        "SELECT COALESCE(SUM(quantity), 0) FROM cart WHERE user_id = $1", user["id"]
    )
    return templates.TemplateResponse(
        "user/dashboard.html",
        {"request": request, "products": products, "cart_count": cart_count}
    )


@app.get("/api/product/search")
async def search_produk(q: str = "", conn=Depends(get_conn)):
    rows = await conn.fetch("""
        SELECT id, product_name, price, quantity, product_picture
        FROM products WHERE product_name ILIKE $1 ORDER BY id
    """, f"%{q}%")
    return [dict(r) for r in rows]


@app.get("/product/{id}", response_class=HTMLResponse)
async def product_detail(request: Request, id: int, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth")

    product = await conn.fetchrow("SELECT * FROM products WHERE id = $1", id)
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    cart_count = await conn.fetchval(
        "SELECT COALESCE(SUM(quantity), 0) FROM cart WHERE user_id = $1", user["id"]
    )
    return templates.TemplateResponse(
        "user/product_detail.html",
        {"request": request, "product": product, "cart_count": cart_count}
    )


@app.get("/dashboard-admin")
async def dashboard_admin(
    request: Request,
    conn=Depends(get_conn),
    user=Depends(admin_required)
):
    total_order = await conn.fetchval("SELECT COUNT(*) FROM orders")
    total_produk = await conn.fetchval("SELECT COUNT(*) FROM products")
    total_user = await conn.fetchval("SELECT COUNT(*) FROM users")
    total_revenue = await conn.fetchval(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'paid'"
    )
    chart_data = await conn.fetch("""
        SELECT DATE(created_at) as tanggal, COUNT(*) as jumlah
        FROM orders WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(created_at) ORDER BY tanggal ASC
    """)
    recent_orders = await conn.fetch("""
        SELECT id, order_code, product_name, total_price, status, created_at, recipient_name
        FROM orders ORDER BY id DESC LIMIT 5
    """)
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request, "user": user,
            "total_order": total_order, "total_produk": total_produk,
            "total_user": total_user, "total_revenue": total_revenue,
            "chart_labels": [str(r["tanggal"]) for r in chart_data],
            "chart_values": [r["jumlah"] for r in chart_data],
            "recent_orders": [dict(r) for r in recent_orders],
        }
    )


@app.get("/product")
async def show_product(request: Request):
    return templates.TemplateResponse("admin/product/main.html", {"request": request})


@app.get("/update-product/{id}")
async def update_product(request: Request, id: int, conn=Depends(get_conn)):
    product = await conn.fetchrow("SELECT * FROM products WHERE id = $1", id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return templates.TemplateResponse(
        "admin/product/update_product.html", {"request": request, "product": product}
    )


@app.post("/api/products")
async def post_products(
    product_name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    product_picture: UploadFile = File(...),
    conn=Depends(get_conn)
):
    import time
    upload_dir = "frontend/src/public/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    ext = product_picture.filename.split(".")[-1]
    filename = f"{int(time.time())}.{ext}"
    with open(f"{upload_dir}/{filename}", "wb") as buffer:
        buffer.write(await product_picture.read())

    await conn.execute(
        "INSERT INTO products (product_name, price, quantity, description, product_picture) VALUES ($1, $2, $3, $4, $5)",
        product_name, price, quantity, description, filename
    )
    return {"msg": "berhasil upload"}


@app.put("/api/products/{id}")
async def update_products(
    id: int,
    product_name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    product_picture: UploadFile = File(None),
    conn=Depends(get_conn)
):
    filename = None
    if product_picture:
        filename = product_picture.filename
        path = f"frontend/src/public/uploads/{filename}"
        os.makedirs("frontend/src/public/uploads", exist_ok=True)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(product_picture.file, buffer)

    await conn.execute("""
        UPDATE products
        SET product_name=$1, price=$2, quantity=$3, description=$4,
            product_picture=COALESCE($5, product_picture)
        WHERE id=$6
    """, product_name, price, quantity, description, filename, id)
    return {"msg": "berhasil update"}


@app.get("/api/products")
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    conn=Depends(get_conn),
):
    offset = (page - 1) * limit
    rows = await conn.fetch(
        "SELECT id, product_name, price, quantity, description, product_picture FROM products ORDER BY id ASC LIMIT $1 OFFSET $2",
        limit, offset
    )
    total_count = await conn.fetchval("SELECT COUNT(*) FROM products")
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    products_list = [dict(row) for row in rows]
    return {"page": page, "limit": limit, "total_items": len(products_list), "total_pages": total_pages, "data": products_list}


@app.delete("/api/products/{id}")
async def delete_products(id: int, conn=Depends(get_conn)):
    await conn.execute("DELETE FROM products WHERE id = $1", id)
    return {"msg": "berhasil delete"}


@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth")

    rows = await conn.fetch("""
        SELECT id, product_name, price, product_picture, quantity, product_id
        FROM cart WHERE user_id = $1 ORDER BY id DESC
    """, user["id"])
    cart_count = await conn.fetchval(
        "SELECT COALESCE(SUM(quantity), 0) FROM cart WHERE user_id = $1", user["id"]
    )
    return templates.TemplateResponse(
        "user/cart.html", {"request": request, "carts": rows, "cart_count": cart_count}
    )


@app.post("/api/cart")
async def add_cart(cart: Cart, request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(401, "Unauthorized")

    existing = await conn.fetchrow(
        "SELECT id, quantity FROM cart WHERE user_id = $1 AND product_id = $2",
        user["id"], cart.product_id
    )
    if existing:
        await conn.execute(
            "UPDATE cart SET quantity = quantity + $1 WHERE id = $2",
            cart.quantity, existing["id"]
        )
    else:
        await conn.execute(
            "INSERT INTO cart (product_name, price, product_picture, quantity, user_id, product_id) VALUES ($1, $2, $3, $4, $5, $6)",
            cart.product_name, cart.price, cart.product_picture, cart.quantity, user["id"], cart.product_id
        )
    return {"msg": "produk ditambahkan ke keranjang"}


@app.put("/api/cart/{id}")
async def update_cart(id: int, data: dict, request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(401, "Unauthorized")

    quantity = data.get("quantity")
    if quantity <= 0:
        await conn.execute("DELETE FROM cart WHERE id = $1 AND user_id = $2", id, user["id"])
        return {"msg": "produk dihapus dari keranjang"}

    await conn.execute(
        "UPDATE cart SET quantity = $1 WHERE id = $2 AND user_id = $3",
        quantity, id, user["id"]
    )
    return {"msg": "quantity diupdate"}


@app.delete("/api/cart/{id}")
async def delete_cart(id: int, conn=Depends(get_conn)):
    await conn.execute("DELETE FROM cart WHERE id = $1", id)
    return {"msg": "berhasil dihapus"}


@app.post("/api/order/status/{id}")
async def update_status(id: int, status: str = Form(...), conn=Depends(get_conn)):
    await conn.execute("UPDATE orders SET status = $1 WHERE id = $2", status, id)
    return RedirectResponse("/manage-orders", status_code=303)


@app.get("/manage-orders")
async def manage_orders(
    request: Request,
    status: str = None,
    conn=Depends(get_conn),
    user=Depends(admin_required)
):
    if status:
        orders = await conn.fetch(
            "SELECT * FROM orders WHERE status = $1 ORDER BY created_at DESC", status
        )
    else:
        orders = await conn.fetch("SELECT * FROM orders ORDER BY created_at DESC")

    return templates.TemplateResponse(
        "admin/order/manageorder.html", {"request": request, "orders": orders}
    )


@app.post("/api/alamat")
async def set_alamat(
    request: Request,
    recipient_address: str = Form(...),
    conn=Depends(get_conn)
):
    user = request.session.get("user")
    if not user:
        raise HTTPException(401, "Unauthorized")

    await conn.execute(
        "INSERT INTO alamat (user_id, recipient_address) VALUES ($1, $2)",
        user["id"], recipient_address
    )
    return {"msg": "alamat berhasil ditambahkan"}


@app.get("/alamat", response_class=HTMLResponse)
async def set_alamat_page(request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth")

    rows = await conn.fetch(
        "SELECT id, recipient_address FROM alamat WHERE user_id = $1 ORDER BY id DESC",
        user["id"]
    )
    return templates.TemplateResponse(
        "admin/set-alamat/set-alamat.html",
        {"request": request, "addresses": [dict(r) for r in rows]}
    )


@app.get("/api/alamat")
async def get_alamat(request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(401, "Unauthorized")

    rows = await conn.fetch(
        "SELECT id, recipient_address FROM alamat ORDER BY id DESC"
    )
    return [dict(r) for r in rows]

@app.put("/api/alamat/{id}")
async def update_alamat(id: int, data: Alamat, request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(401, "Unauthorized")

    await conn.execute(
        "UPDATE alamat SET recipient_address = $1 WHERE id = $2 AND user_id = $3",
        data.recipient_address, id, user["id"]
    )
    return {"msg": "alamat berhasil diupdate"}


@app.delete("/api/alamat/{id}")
async def delete_alamat(id: int, request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(401, "Unauthorized")

    await conn.execute(
        "DELETE FROM alamat WHERE id = $1 AND user_id = $2", id, user["id"]
    )
    return {"msg": "alamat berhasil dihapus"}


@app.post("/api/order")
async def order_items(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
    recipient_name: str = Form(...),
    recipient_address: str = Form(...),
    patokan: str = Form(...),
    payment_picture: UploadFile = File(...),
    conn=Depends(get_conn)
):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user["id"]

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity harus lebih dari 0")

    upload_dir = "frontend/src/public/payments"
    os.makedirs(upload_dir, exist_ok=True)
    ext = payment_picture.filename.split(".")[-1]
    file_name = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(upload_dir, file_name), "wb") as buffer:
        buffer.write(await payment_picture.read())

    order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    async with conn.transaction():
        product = await conn.fetchrow(
            "SELECT id, product_name, price, quantity, product_picture FROM products WHERE id = $1 FOR UPDATE",
            product_id
        )
        if not product:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        if product["quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Stok tidak cukup")

        total_price = float(product["price"]) * quantity

        await conn.execute(
            "UPDATE products SET quantity = quantity - $1 WHERE id = $2",
            quantity, product_id
        )

        new_order = await conn.fetchrow("""
            INSERT INTO orders (
                product_id, product_name, price, quantity,
                recipient_name, recipient_address, total_price,
                product_picture, payment_picture, patokan,
                user_id, status, shipping_status, order_code, created_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
            RETURNING *
        """,
            product_id, product["product_name"], product["price"], quantity,
            recipient_name, recipient_address, total_price,
            product["product_picture"], file_name, patokan,
            user_id, "pending", "processing", order_code, datetime.now()
        )

        await conn.execute(
            "DELETE FROM cart WHERE product_id = $1 AND user_id = $2",
            product_id, user_id
        )

    return {"msg": "Order berhasil dibuat", "order_code": order_code, "data": dict(new_order)}


@app.get("/api/orders/history")
async def get_order_history(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    conn=Depends(get_conn),
):
    rows = await conn.fetch(
        "SELECT * FROM orders WHERE user_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3",
        user_id, limit, offset
    )
    return [dict(row) for row in rows]


@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth")

    rows = await conn.fetch(
        "SELECT id, product_name, price, quantity, product_id FROM cart WHERE user_id = $1 ORDER BY id DESC",
        user["id"]
    )
    carts = [dict(r) for r in rows]
    for item in carts:
        item["price"] = float(item["price"])
    total = sum(item["price"] * item["quantity"] for item in carts)

    return templates.TemplateResponse(
        "user/checkout.html", {"request": request, "carts": carts, "total": total}
    )


@app.get("/order", response_class=HTMLResponse)
async def order_page(request: Request, conn=Depends(get_conn)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth")

    rows = await conn.fetch(
        "SELECT * FROM orders WHERE user_id = $1 ORDER BY id DESC", user["id"]
    )
    orders = [dict(r) for r in rows]
    total = sum(float(o["total_price"]) for o in orders)

    return templates.TemplateResponse(
        "user/order.html",
        {"request": request, "orders": orders, "total": total, "cart_count": 0}
    )