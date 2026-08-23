#jwt imports
from jose import jwt, JWTError
#quering imports
from app.database import get_db
import app.models  as models
from sqlalchemy.orm import session
#fastapi imports
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
#utils import
from app.config import settings
from datetime import datetime, timezone, timedelta
import app.schemas as  schemas
access_token = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(payload: schemas.Payload):
    #add exp_time to payload
    CopyPayload = payload.copy()
    CopyPayload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #create and return token
    token = jwt.encode(CopyPayload, SECRET_KEY, algorithm=ALGORITHM)
    return token

#verifing  the token
def verfiy_access_token(token, httpexception):
    try:
        decoded_token = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        #get the id  from the token and return it
        id = decoded_token.get("id")
        if not id:
            raise httpexception
        return id
    except JWTError:
        raise httpexception
#to get the current user
def get_current_user(token_dependency = Depends(access_token), db: session = Depends(get_db)):
    user_id = verfiy_access_token(token=token_dependency, 
                                  httpexception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"}
))
    the_user =  db.query(models.User).filter(models.User.id == user_id).first()
    return the_user