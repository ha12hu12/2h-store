import pytest
#app. imports
from app.config import settings
from app.main import twoH
from app.database import get_db, Base
import app.schemas as schemas
from app.oauth2 import create_access_token
import app.models as models
import app.utils as  utils
#fast api
from fastapi.testclient import TestClient
#sql alchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


#Create engine
SQL_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'
engine = create_engine(SQL_DATABASE_URL)
#Create a sessions factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False ,bind=engine)

#data for creating the test account, im putting it here so i can import it in the "user_testing" file
data1= {
            "username": "ha12hu12_tester1",
            "password": "ha12hu12"
        }
@pytest.fixture
def session():
    Base.metadata.drop_all(bind = engine)
    Base.metadata.create_all(bind = engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    twoH.dependency_overrides[get_db] = override_get_db
    yield TestClient(app=twoH)


#author.. fixtures
@pytest.fixture
def token(create_test_user1):
    return create_access_token(payload={"id": create_test_user1.id})

@pytest.fixture
def authorized_client(client, token):
    client.headers={
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def create_test_user1(session):
    #if you change the password make sure to change it in user_testing -> test5

    
    new_user = models.User(**data1)
    new_user.password = utils.hash_password(password = new_user.password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    the_new_user = session.query(models.User).filter(models.User.username == data1["username"]).first()
    assert the_new_user.username == data1['username']  
    assert utils.verify_password(plain_password=data1['password'], 
                                 hashed_password=the_new_user.password)  == True
    return new_user