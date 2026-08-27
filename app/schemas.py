from pydantic import BaseModel
from datetime import datetime
from typing import Optional
#--------user schemas--------#
class UserCreate(BaseModel):
    username: str
    password: str
class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True
class UserUpdateUsername(BaseModel):
    username:str
class UserUpdatePassword(BaseModel):
    current_password:str
    new_password:str

#--------auth schemas--------#
class UserLogin(BaseModel):
    username: str
    password: str
class Payload(BaseModel):
    id: int



#--------product schemas--------#
class ProductCreate(BaseModel):
    product_name: str
    description: Optional[str] = "there is no description"
    amount: int
    price: int
    image_url: Optional[str] = "there is no images"

class ProductOut(BaseModel):
    product_name: str
    description: str
    amount: int
    image_url: Optional[str] = None 
    price: float
    owner: UserOut
    
class MyProductOut(BaseModel):
    product_name: str
    description: Optional[str] = "there is no description"
    amount: int
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[int] = None
    price: Optional[float] = None   