from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(
    tags=["Device Token"]
)

@router.post("/device-token")
def save_device_token(
    token_data: schemas.DeviceTokenCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # نشوف هل الـ token موجود أصلاً
    existing = db.query(models.DeviceToken).filter(
        models.DeviceToken.token == token_data.token
    ).first()

    # لو موجود، ما نسوي شي
    if existing:
        return {"message": "token already exists"}

    # لو ما موجود، نحفظه
    new_token = models.DeviceToken(
        user_id=current_user.id,
        token=token_data.token
    )
    db.add(new_token)
    db.commit()

    return {"message": "token saved"}