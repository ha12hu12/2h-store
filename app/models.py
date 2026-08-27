from .database import Base
from sqlalchemy import Column, Integer, String, VARCHAR, Float, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(50), nullable=False, unique=True)
    password = Column(String, nullable=False)
    cash = Column(Float, server_default=text("0.0"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
                        server_default=text("now()"))


class product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    product_name = Column(VARCHAR(length=100), nullable=False)
    description = Column(VARCHAR(1000), server_default="No description")
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String, server_default=None)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
                        server_default=text("now()"))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), 
                      nullable=False)

    owner = relationship("User")

class cart(Base):
    __tablename__ = "cart"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), 
                     primary_key=True)
    post_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), 
                     primary_key=True)
