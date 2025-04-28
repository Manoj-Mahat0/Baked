from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Category, Product, Store
from schemas import CategoryCreate, ProductCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/category/add")
def add_category(category: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(Category).filter_by(name=category.name, store_id=category.store_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists for this store")

    new_cat = Category(**category.dict())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.post("/product/add")
def add_product(payload: ProductCreate, db: Session = Depends(get_db)):
    # Check if category exists
    category = db.query(Category).filter(Category.id == payload.category_id, Category.store_id == payload.store_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found for this store.")

    # Check if store exists
    store = db.query(Store).filter(Store.id == payload.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    # Create product
    new_product = Product(
        name=payload.name,
        price=payload.price,
        category_id=payload.category_id,
        store_id=payload.store_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "id": new_product.id,
        "name": new_product.name,
        "price": new_product.price,
        "store_id": new_product.store_id,
        "category_id": new_product.category_id
    }


@router.get("/products/{store_id}")
def get_products_by_store(store_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter_by(store_id=store_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category.name if p.category else None
        }
        for p in products
    ]

# ✅ Get all categories
@router.get("/categories")
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "store_id": cat.store_id
        }
        for cat in categories
    ]

# ✅ Get all products
@router.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category_id": p.category_id,
            "store_id": p.store_id
        }
        for p in products
    ]

@router.get("/categories/{store_id}")
def get_categories_by_store(store_id: int, db: Session = Depends(get_db)):
    categories = db.query(Category).filter(Category.store_id == store_id).all()

    if not categories:
        return {"message": "No categories found for this store."}

    category_list = []
    for c in categories:
        category_list.append({
            "id": c.id,
            "name": c.name,
            "store_id": c.store_id
        })

    return category_list
