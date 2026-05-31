from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

async def auth_middleware(request: Request, call_next):

    protected_routes = [
        "/dashboard",
        "/product",
        "/cart",    
        "/checkout",
        "/order",
        
    ]

    admin_routes = [
        "/dashboard-admin",
        "/list-users",
        "/list-product",
        "/manage-orders",
        "/add-product",
        "/update-product", 
        "/alamat",    
        "/add-product",
        "/update-product",

    ]

    path = request.url.path
    user = request.session.get("user")

    # wajib login
    if any(path.startswith(route) for route in protected_routes + admin_routes):
        if not user:
            return RedirectResponse("/auth", status_code=302)

    # wajib admin
    if any(path.startswith(route) for route in admin_routes):
        if user.get("role") != "admin":
            return RedirectResponse("/dashboard", status_code=302)

    return await call_next(request)

async def auth_required(request: Request):
    user = request.session.get("user")

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return user


async def admin_required(request: Request):
    user = request.session.get("user")

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return user