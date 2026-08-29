from app.oauth2 import create_access_token
import app.models as models


# ==== CREATE (POST /carts/{id}) ====

def test_create_cart_insufficient_funds(authorized_client, test_products, create_test_user2):
    product = next(p for p in test_products if p.owner_id == create_test_user2.id)
    res = authorized_client.post(f"/carts/{product.id}")
    assert res.status_code == 409


def test_create_cart_success(authorized_client, test_products, create_test_user1, create_test_user2, session):
    product = next(p for p in test_products if p.owner_id == create_test_user2.id)
    create_test_user1.money = 1000.0
    session.commit()
    res = authorized_client.post(f"/carts/{product.id}")
    assert res.status_code == 201


def test_create_cart_product_not_found(authorized_client):
    res = authorized_client.post("/carts/99999")
    assert res.status_code == 404


def test_create_cart_already_exists(authorized_client, test_products, create_test_user1, create_test_user2, session):
    product = next(p for p in test_products if p.owner_id == create_test_user2.id)
    create_test_user1.money = 1000.0
    session.commit()
    res1 = authorized_client.post(f"/carts/{product.id}")
    assert res1.status_code == 201
    res2 = authorized_client.post(f"/carts/{product.id}")
    assert res2.status_code == 409


def test_create_cart_out_of_stock(authorized_client, session, create_test_user1, create_test_user2):
    product = models.product(
        product_name="Sold Out Item", description="none",
        amount=0, price=10.0, owner_id=create_test_user2.id
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    product_id = product.id

    create_test_user1.money = 1000.0
    session.commit()
    res = authorized_client.post(f"/carts/{product_id}")
    assert res.status_code == 409


# ==== GET MY PURCHASES ====

def test_get_my_purchases(authorized_client, create_test_cart):
    product_name = create_test_cart.product.product_name
    res = authorized_client.get("/carts/me")
    assert res.status_code == 200
    result = res.json()
    assert len(result) == 1
    assert result[0]['product']['product_name'] == product_name


def test_get_my_purchases_empty(authorized_client):
    res = authorized_client.get("/carts/me")
    assert res.status_code == 200
    assert res.json() == []


# ==== GET UNPAID SELLS (debts) ====

def test_get_unpaid_sells(client, create_test_user1, create_test_user2, create_test_cart):
    user1_username = create_test_user1.username
    token2 = create_access_token(payload={"id": create_test_user2.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token2}"}
    res = client.get("/carts/unpaid_sells")
    assert res.status_code == 200
    result = res.json()
    assert len(result) == 1
    assert result[0]['buyer']['username'] == user1_username


def test_get_unpaid_sells_none(authorized_client):
    res = authorized_client.get("/carts/unpaid_sells")
    assert res.status_code == 404


def test_get_unpaid_sells_filter_username(client, create_test_user1, create_test_user2, create_test_cart):
    user1_username = create_test_user1.username
    token2 = create_access_token(payload={"id": create_test_user2.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token2}"}

    res_match = client.get(f"/carts/unpaid_sells?username={user1_username}")
    assert res_match.status_code == 200
    assert len(res_match.json()) == 1

    res_no_match = client.get("/carts/unpaid_sells?username=nonexistent")
    assert res_no_match.status_code == 200
    assert res_no_match.json() == []


# ==== PATCH (mark as paid) ====

def test_mark_paid_success(client, session, create_test_user2, create_test_cart):
    cart_id = create_test_cart.id
    token2 = create_access_token(payload={"id": create_test_user2.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token2}"}
    res = client.patch("/carts", json={"cart_id": cart_id, "status": True})
    assert res.status_code == 201

    remaining = session.query(models.Cart).filter(models.Cart.id == cart_id).first()
    assert remaining is None


def test_mark_paid_not_owner(authorized_client, create_test_cart):
    cart_id = create_test_cart.id
    res = authorized_client.patch("/carts", json={"cart_id": cart_id, "status": True})
    assert res.status_code == 403


def test_mark_paid_not_found(authorized_client):
    res = authorized_client.patch("/carts", json={"cart_id": 9999, "status": True})
    assert res.status_code == 404


# ==== DELETE ====

def test_delete_cart_owner(authorized_client, create_test_cart):
    res = authorized_client.delete(f"/carts/{create_test_cart.id}")
    assert res.status_code == 200


def test_delete_cart_not_owner(client, create_test_user2, create_test_cart):
    cart_id = create_test_cart.id
    token2 = create_access_token(payload={"id": create_test_user2.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token2}"}
    res = client.delete(f"/carts/{cart_id}")
    assert res.status_code == 403


def test_delete_cart_not_found(authorized_client):
    res = authorized_client.delete("/carts/9999")
    assert res.status_code == 404