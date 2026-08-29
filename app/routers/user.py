#fast api import
from fastapi import APIRouter, Depends, HTTPException, status
#sql alchemy import
from sqlalchemy.orm import session
#database import
from app.database import get_db
#schemas import
import app.schemas as schemas
#models import
import app.models as models
#utils import
import app.utils as utils
from app.oauth2 import get_current_user
router = APIRouter(tags=["user"])

@router.post('/users', response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: schemas.UserCreate, db: session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"account with user:{data.username} already exist.")

    new_user = models.User(**data.model_dump())

    new_user.password = utils.hash_password(password = new_user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/me", response_model=schemas.UserOut)
def get_me(current_user = Depends(get_current_user)):
    return current_user

#update user
  #update username
@router.put("/users/username", status_code=status.HTTP_201_CREATED)
def update_user_username(updated_username: schemas.UserUpdateUsername , db: session = Depends(get_db), current_user = Depends(get_current_user)):
    the_user = db.query(models.User).filter(models.User.id == current_user.id)
    the_user.update(updated_username.model_dump(), synchronize_session = False)
    db.commit()
    return {"message": "username updated successfully", "new_username": updated_username.username}

  #update password
@router.put("/users/password", status_code=status.HTTP_201_CREATED)
def update_password(updated_password: schemas.UserUpdatePassword , db: session = Depends(get_db), current_user = Depends(get_current_user)):
    the_user = db.query(models.User).filter(models.User.id == current_user.id)

    #check if he entered the right current_password
    if not utils.verify_password(plain_password=updated_password.current_password, hashed_password=the_user.first().password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="incorrect current password")

    #if he did: change the password for him and return
    hashed_password = utils.hash_password(password=updated_password.new_password)
    the_user.update({"password":hashed_password}, synchronize_session = False)
    db.commit()
    return {"message": "successfully changed password"}

  #update cash
@router.put("/users/money", status_code=status.HTTP_201_CREATED)
def update_user_money(updated_money: schemas.UserUpdateMoney , db: session = Depends(get_db), current_user = Depends(get_current_user)):
    the_user = db.query(models.User).filter(models.User.id == current_user.id)
    the_user.update(updated_money.model_dump(), synchronize_session = False)
    db.commit()
    return {"message": "money updated successfully", 
            "new_money": updated_money}



#delete user
@router.delete("/users")
def delete_user(db: session = Depends(get_db), current_user = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "user deleted successfully", "username": current_user.username}