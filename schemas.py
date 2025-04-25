from typing import Optional
from pydantic import BaseModel
from datetime import date

class MainStoreBase(BaseModel):
    name: str

class MainStoreCreate(MainStoreBase):
    pass

class StoreBase(BaseModel):
    name: str
    location: str
    address: str
    phone_number: str
    dob: date

class StoreCreate(BaseModel):
    name: str
    location: str
    address: str
    phone_number: str
    dob: date
    mainstore_id: Optional[int] = None  # ✅ Accepts null now


class UserBase(BaseModel):
    full_name: str
    phone_number: str
    dob: date

class UserCreate(UserBase):
    store_id: int

class UserLogin(BaseModel):
    phone_number: str
    dob: date

class CategoryCreate(BaseModel):
    name: str
    store_id: int

class ProductCreate(BaseModel):
    name: str
    price: int
    category_id: int
    store_id: int

class PurchaseRequest(BaseModel):
    phone_number: str
    unique_code: str
    product_id: int
    use_loyalty_points: int  # how many points user wants to apply (max 50)

