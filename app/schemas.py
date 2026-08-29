from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


#--------user schemas--------#
class UserCreate(BaseModel):
    username: str
    password: str
class UserOut(BaseModel):
    id: int
    username: str
    money: float
    model_config = ConfigDict(from_attributes=True)

class UserUpdateUsername(BaseModel):
    username:str

class UserUpdateMoney(BaseModel):
    money: int

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
    price: float
    image_url: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    product_name: str
    description: str
    amount: int
    image_url: Optional[str] = None 
    price: float
    owner: UserOut
    
class MyProductOut(BaseModel):
    id: int
    product_name: str
    description: Optional[str] = "there is no description"
    amount: int
    price: float
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[int] = None
    price: Optional[float] = None 
    image_url: Optional[str] = None  

#--------cart schemas--------#
class ChangePaid(BaseModel):
    cart_id: int
    status: bool

class CartOutPurchases(BaseModel):
    id: int
    product: ProductOut
    status: bool

class CartOutDebts(BaseModel):
    id: int
    buyer: UserOut
    product: ProductOut
    status: bool