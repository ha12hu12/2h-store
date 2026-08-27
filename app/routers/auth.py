from fastapi import APIRouter,HTTPException,status
#fast api import
from fastapi import APIRouter, Depends, HTTPException, status
#sql alchemy import
from sqlalchemy.orm import session
#database import
from app.database import get_db
#schemas import
from app.schemas import UserLogin
#models import
import app.models as models
from app.oauth2 import create_access_token
import app.utils as utils
router = APIRouter(tags=["auth"])

@router.post("/login")
def login(data:UserLogin, db:session = Depends(get_db)):
    the_user = db.query(models.User).filter(models.User.username == data.username).first()
    #check if account is there
    if not the_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"there is no user with {data.username} username")
    #check if the password is correct
    if not utils.verify_password(plain_password=data.password, hashed_password=the_user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials")

    access_token = create_access_token(payload={"id": the_user.id})
    return {"access_token": access_token, "token_type": "bearer"}