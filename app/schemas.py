from pydantic import BaseModel
from datetime import datetime
#user schemas
class UserCreate(BaseModel):
    username: str
    password: str
class UserOut(BaseModel):
    username: str
    created_at: datetime
class UserUpdateUsername(BaseModel):
    username:str
class UserUpdatePassword(BaseModel):
    current_password:str
    new_password:str

  #auth schemas
class UserLogin(BaseModel):
    username: str
    password: str
class Payload(BaseModel):
    id: int