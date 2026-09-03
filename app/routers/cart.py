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
import app.models as models
from app.oauth2 import get_current_user
from typing import List
from app.routers.product import delete_product
router = APIRouter(tags=["cart"])

@router.post("/carts/{id}", status_code=status.HTTP_201_CREATED)
def create_cart_product(id: int, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    the_product = db.query(models.product).filter(models.product.id == id).first()

    #check if product exist
    if not the_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"there is no product with id: {id}")

    #the same user should be able to add the same thing 2 times or more
    
    #check if product amount is enough
    if the_product.amount == 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail=f"the product is out! - sry")
    #check if user have cash to buy this
    if current_user.money < the_product.price:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail=f"you dont have enough cash to buy: {the_product.product_name}")

                        
    #نقص the amount of the product
    the_product.amount = the_product.amount - 1
    # نقص the price of the product from the user cash

    new_cash = current_user.money - the_product.price
    current_user.money = new_cash

    
    
    #add the new purchase to cart
    new_cart_product = models.Cart(user_id= current_user.id,
                                       product_id= the_product.id)
    db.add(new_cart_product)
    db.commit()
    db.refresh(new_cart_product)

    return {"message": f"product: {the_product.product_name} was successfully added to the user: {current_user.username} cart.",
                    "new user cash": f"and successfully changed user cash to {current_user.money}"}

@router.post("/carts/pledges/{product_id}", status_code=status.HTTP_201_CREATED)
def create_cart_pledge(product_id: int, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    the_product = db.query(models.product).filter(models.product.id == product_id).first()
    
    #check if pledge exist
    if not the_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"there is no product with id: {product_id}")
    #check if cart is pledge
    if not the_product.pledge_shares:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="this is not a pledge product")
    
    if current_user.username not in the_product.pledge_shares :
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="you are not part of pledge")

    user_pledge = the_product.pledge_shares[current_user.username]
    if current_user.money < user_pledge:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail=f"you dont have enough cash to put in pledge: {the_product.product_name}")
    #check if pledges is not more than product price
    existing_carts = db.query(models.Cart).filter(
    models.Cart.product_id == product_id
).all()

    total_pledges = 0

    for cart in existing_carts:
        user = db.query(models.User).filter(
            models.User.id == cart.user_id
        ).first()

        total_pledges += the_product.pledge_shares[user.username]


        user_pledge = the_product.pledge_shares[current_user.username]

    if total_pledges + user_pledge > the_product.price:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="pledge amount exceeds product price"
        )
    current_user.money -= user_pledge
    new_cart_product = models.Cart(user_id= current_user.id,
                                       product_id= the_product.id)
    db.add(new_cart_product)
    db.commit()
    db.refresh(new_cart_product)
    return {"message": f"product: {the_product.product_name} was successfully added to the user: {current_user.username} cart.",
                        "new user cash": f"and successfully -: {the_product.pledge_shares[current_user.username]} from  the  user"}

@router.get("/carts/me",  response_model=List[schemas.CartOutPurchases])
def get_my_purchases(current_user=Depends(get_current_user), db=Depends(get_db)):
    purchases =  db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id).all()

    for purchase in purchases:
        the_product = db.query(models.product).filter(models.product.id == purchase.product_id).first()
        if the_product.pledge_shares:
            the_product.pledge_shares = {current_user.username: the_product.pledge_shares[current_user.username]}
    return purchases

#this is to get all the product that is not paid to the seller to see
#which means: getting debts,
#or: getting_unpaid_sells
@router.get("/carts/unpaid_sells", response_model=List[schemas.CartOutDebts])
def get_unpaid_sells(username: str = None, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    products = db.query(models.Cart).join(
    models.product, models.Cart.product_id == models.product.id
).join(
    models.User, models.Cart.user_id == models.User.id
).filter(
    models.product.owner_id == current_user.id,
    models.Cart.status == False
)
    

    if not products.all():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"you have no debts")
    
    if username:
        products = products.filter(models.User.username.ilike(f"%{username}%"))
    return products


@router.patch("/carts", status_code=status.HTTP_201_CREATED)
def change_paid_product(data: schemas.ChangePaid, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    cart_product_query = db.query(models.Cart).filter(models.Cart.id == data.cart_id)
    if not cart_product_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,   detail="not  found")

    the_product = db.query(models.product).filter(models.product.id == cart_product_query.first().product_id).first()

    #check if the user altering "paid" is the product owner
    if current_user.id != the_product.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"user: {current_user.username} is not allowed to alter paid")
    #give the owner his bucks🤑
    if not the_product.pledge_shares:
        current_user.money += the_product.price

    #check if its pledge and do what supposed to happen
    if the_product.pledge_shares:
            the_user  = db.query(models.User).filter(models.User.id ==  cart_product_query.first().user_id).first()
            user_pledge= the_product.pledge_shares[the_user.username]
            the_product.price -= user_pledge
            current_user.money +=user_pledge
            if the_product.price <= 0:
                db.delete(the_product)
                db.commit()

    #delete the product  from cart
    if data.status == True:
        cart_product_query.delete(synchronize_session=False)
        db.commit()


    return {"message": "successfully updated paid",
            "new_cart": cart_product_query.first()}


@router.delete("/carts/{id}")
def delete_cart(id: int, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    cart_query = db.query(models.Cart).filter(models.Cart.id == id)
    if not cart_query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    the_product = db.query(models.product).filter(models.product.id == cart_query.first().product_id).first()


    if cart_query.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"user: {current_user.id} cant change: {cart_query.first().user_id}")
    if not the_product.pledge_shares:
        the_product.amount += 1
    current_user.money += the_product.price
    cart_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "deleted successfully"}