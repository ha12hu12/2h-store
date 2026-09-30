from app.routers import user, auth, product, cart, device_token

from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

twoH = FastAPI()

origins = ["http://localhost:5174","http://localhost:5173", "https://2h-store-frontend.vercel.app"]

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
twoH.include_router(cart.router)
twoH.include_router(device_token.router)


@twoH.get("/loaderio-0146f5ac8e18116efede814f9dffd1aa.txt", response_class=PlainTextResponse)
@twoH.get("/loaderio-0146f5ac8e18116efede814f9dffd1aa/", response_class=PlainTextResponse)
def loaderio_verify():
    return "loaderio-0146f5ac8e18116efede814f9dffd1aa"