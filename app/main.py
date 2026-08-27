from app.routers import user, auth, product

from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware

twoH = FastAPI()

origins = ["*"]

twoH.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@twoH.get("/")
def root():
    return "root"

twoH.include_router(user.router)
twoH.include_router(auth.router)
twoH.include_router(product.router)