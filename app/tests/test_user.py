import app.schemas as schemas
from datetime import datetime
import app.tests.conftest as conftest
import app.utils as utils
import app.models as models
#test user create
def test1(client):
    data= {
        "username": "ha12hu12",
        "password": "ha12hu12"
    }

    res = client.post("/users", json=data)
    new_user = schemas.UserOut(**res.json())
    assert res.status_code == 201
    assert new_user.username == data['username']

#test create already exist user
def test2(create_test_user1, client):
    res = client.post("/users", json=conftest.data1)
    assert res.status_code == 409
    assert res.json() == {"detail": f"account with user:{conftest.data1['username']} already exist."}



#test user update username
def test3(authorized_client):
    data={
        "username": "hehe"
    }
    res = authorized_client.put("/users/username", json=data)

    assert res.status_code == 201
    assert res.json() == {"message": "username updated successfully", "new_username": data["username"]}

  #test unauthorized user update username
def test4(client):
    res = client.put("/users/username", json="data")

    assert res.status_code == 401
    assert res.json() == {'detail': 'Not authenticated'}



#test authorized user update password
def test5(authorized_client, session):
    data={
        "current_password": conftest.data1['password'],
        "new_password": "1000"
    }
    res = authorized_client.put("/users/password", json=data)

    assert res.status_code == 201
    assert res.json() == {"message": "successfully changed password"}
    the_user = session.query(models.User).filter(models.User.username == conftest.data1['username']).first()
    assert utils.verify_password(plain_password= data['new_password'],
                                 hashed_password= the_user.password)
  #test user enters wrong password to update password
def test6(authorized_client, session):
    data={
        "current_password": "WRONG_current_password👺👺",
        "new_password": "1000"
    }
    res = authorized_client.put("/users/password", json=data)

    assert res.status_code == 403
    assert res.json() == {"detail": "incorrect current password"}

  #test unauthorized user update password
def test7(client):
    res = client.put("/users/password", json="data")
    
    assert res.status_code == 401
    assert res.json() == {'detail': 'Not authenticated'}

#test user delete
def test8(create_test_user1, authorized_client):
    res = authorized_client.delete("/users")

    assert res.status_code == 200
    assert res.json() == {"message": "user deleted successfully", "username": conftest.data1['username']}