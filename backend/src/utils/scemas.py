from pydantic import BaseModel
<<<<<<< HEAD
from typing import Literal, Optional
from datetime import datetime


class Products(BaseModel):
=======


class Products(BaseModel):
    id: int | None = None
>>>>>>> 3fe070cb4d321a56b6fa04e374161ddb5bf0094c
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
<<<<<<< HEAD
    role: Literal["admin", "user"] = "user"
    


class Orders(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int

    recipient_name: str
    recipient_address: str

    total_price: float

    product_picture: str
    payment_picture: str

    user_id: int

    status: str = "pending"
    shipping_status: str = "processing"
    patokan: str


    order_code: Optional[str] = None
    created_at: Optional[datetime] = None
    
class Cart(BaseModel):
    id: Optional[int] = None
=======
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
>>>>>>> 3fe070cb4d321a56b6fa04e374161ddb5bf0094c
    product_name: str
    price: float
    product_picture: str
    quantity: int
    user_id: int
    product_id: int
<<<<<<< HEAD
    
class Alamat(BaseModel):
    recipient_address: str
=======
>>>>>>> 3fe070cb4d321a56b6fa04e374161ddb5bf0094c
