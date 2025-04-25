from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import random


# class MainStore(Base):
#     __tablename__ = "mainstores"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)

#     stores = relationship("Store", back_populates="mainstore")


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    mainstore_id = Column(Integer, ForeignKey("stores.id"), nullable=True)  # self-referencing FK

    parent_store = relationship("Store", remote_side=[id], backref="substores")
    users = relationship("User", back_populates="store")




class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True)
    dob = Column(Date)
    store_id = Column(Integer, ForeignKey("stores.id"))
    loyalty_points = Column(Integer, default=50)  # ✅ Default 50
    unique_code = Column(String(4), unique=True, index=True)  # ✅ 4-digit code

    store = relationship("Store", back_populates="users")
    purchases = relationship("Purchase", back_populates="user")

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    purchase_date = Column(Date)

    user = relationship("User", back_populates="purchases")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"))

    store = relationship("Store")
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))

    store = relationship("Store")
    category = relationship("Category", back_populates="products")

