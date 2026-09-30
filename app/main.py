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


from fastapi.responses import PlainTextResponse

# استخدم اسم متغير تطبيق FastAPI الخاص بك (عادة app)
@twoH.get("/loaderio-6389923698787af9dfc4f5f1c3269d1b.txt", response_class=PlainTextResponse)
@twoH.get("/loaderio-6389923698787af9dfc4f5f1c3269d1b/", response_class=PlainTextResponse)
def stuff_pls_work():
    return "loaderio-6389923698787af9dfc4f5f1c3269d1b"