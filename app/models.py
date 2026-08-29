from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, VARCHAR, Float, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(50), nullable=False, unique=True)
    password = Column(String, nullable=False)
    money = Column(Float, server_default=text("0.0"), nullable=False)
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

from sqlalchemy import UniqueConstraint

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    status = Column(Boolean, server_default=text("False"), nullable=False)

    buyer = relationship("User")
    product = relationship("product")
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='unique_user_product'),
    )


