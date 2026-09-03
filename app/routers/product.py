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

router = APIRouter(tags=["products"])

#create product
@router.post("/products", status_code=status.HTTP_201_CREATED, response_model= schemas.ProductOut)
def create_product(product_data: schemas.ProductCreate ,db: session = Depends(get_db), current_user = Depends(get_current_user)):
    new_product = models.product(**product_data.model_dump())
    new_product.owner_id = current_user.id
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

#get  products
@router.get("/products", response_model= List[schemas.ProductOut])
def get_products(db: session = Depends(get_db), current_user = Depends(get_current_user)):
    all_products = db.query(models.product).all()

    #check if it was pledge, if it is show its price
    for product in all_products:
        if not product.pledge_shares:
            continue
        if product.owner_id == current_user.id:
            continue
        if current_user.username in product.pledge_shares:
            product.pledge_shares = {current_user.username: product.pledge_shares[current_user.username]}
        else:
            product.pledge_shares = None
    if not all_products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="there is no products in the database")
    return all_products

  #get MY products
@router.get("/products/my", response_model= List[schemas.MyProductOut])
def get_MY_products(db: session = Depends(get_db), current_user = Depends(get_current_user)):
    products = db.query(models.product).filter(models.product.owner_id == current_user.id).all()

    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"you have no products.")
    return products

  #get product by name
@router.get("/products/{name}", response_model= List[schemas.ProductOut])
def get_product_byName(name: str, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    the_product = db.query(models.product).filter(models.product.product_name.ilike(f"%{name}%")).all()
    if not the_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"there is no product with name: '{name}'")
    return the_product


#update product
@router.patch("/products/{name}")
def update_product(name: str, updated_product: schemas.ProductUpdate, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    product_query = db.query(models.product).filter(models.product.product_name == name)
    the_product = product_query.first()

    if not the_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product found with id: {id}")

    if current_user.id != the_product.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to edit this product")

    if not the_product.pledge_shares:
        if updated_product.pledge_shares:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this is not a pledge product")
        
    update_data = updated_product.model_dump(exclude_unset=True)
    product_query.update(update_data, synchronize_session=False)
    db.commit()
    return {"message": "product updated successfully",
            "updated_data": update_data}



#delete product
@router.delete("/products/{name}")
def delete_product(name: str, db: session = Depends(get_db), current_user = Depends(get_current_user)):
    
    product_query = db.query(models.product).filter(models.product.product_name == name)
    the_product = product_query.first()

    if not the_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"there is no product with name: '{name}'")
        
    if current_user.id != the_product.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you cant delete this product bc its not yours")

    product_query.delete(synchronize_session = False)
    db.commit()
    return {"message": f"product: '{name}' was deleted successfully"}