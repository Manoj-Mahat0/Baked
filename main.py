from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine

# Import routers
from routers import auth, store, user, product, purchase

app = FastAPI()

# Create all MySQL tables
Base.metadata.create_all(bind=engine)

# Allow all CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(store.router, prefix="/store", tags=["Store"])
app.include_router(user.router, tags=["User"])
app.include_router(product.router, tags=["Product & Category"])
app.include_router(purchase.router, tags=["Purchase"])

@app.get("/")
def read_root():
    return {"message": "🎉 API is running!"}
