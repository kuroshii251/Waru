from pydantic import BaseModel


class Products(BaseModel):
    id: int | None = None
    product_name: str
    price: float
    quantity: int
    description: str
    product_picture: str


class Users(BaseModel):
    name: str
    phone: int
    email: str
    password: str
    address: str | None = None


class Orders(BaseModel):
    id: int | None = None
    product_name: str
    price: float
    quantity: int
    recipient_name: str
    recipient_address: str
    total_price: float
    product_picture: str
    user_id: int


class Cart(BaseModel):
    id: int | None = None
    product_name: str
    price: float
    product_picture: str
    quantity: int
    user_id: int
    product_id: int
