from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse


async def auth_middleware(request: Request, call_next):
 
    protected_routes = ["/dashboard", "/product"]

    path = request.url.path
    is_protected = any(path.startswith(route) for route in protected_routes)

    if is_protected:
        user = request.session.get("user")
        if not user:
            return RedirectResponse(url="/auth", status_code=302)

    response = await call_next(request)
    return response


async def auth_required(request: Request):
 
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user