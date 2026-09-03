from app.oauth2 import create_access_token


def test_create_product(authorized_client, create_test_user1):
    data = {
        "product_name": "Keyboard",
        "description": "Mechanical keyboard",
        "amount": 10,
        "price": 120.0
    }
    res = authorized_client.post("/products", json=data)
    assert res.status_code == 201
    new_product = res.json()
    assert new_product['product_name'] == data['product_name']
    assert new_product['description'] == data['description']
    assert new_product['amount'] == data['amount']
    assert new_product['price'] == data['price']
    assert new_product['owner']['id'] == create_test_user1.id


def test_create_product_unauthorized(client):
    data = {
        "product_name": "Keyboard",
        "description": "Mechanical keyboard",
        "amount": 10
    }
    res = client.post("/products", json=data)
    assert res.status_code == 401


def test_get_all_products(authorized_client, test_products):
    res = authorized_client.get("/products")
    assert res.status_code == 200
    assert len(res.json()) == len(test_products)


def test_get_all_products_empty(authorized_client):
    res = authorized_client.get("/products")
    assert res.status_code == 404


def test_get_all_products_pledge_owner_sees_all_shares(client, create_test_pledge_product, create_test_user2):
    token = create_access_token(payload={"id": create_test_user2.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.get("/products")

    assert res.status_code == 200
    pledge_product = next(item for item in res.json() if item["id"] == create_test_pledge_product.id)
    assert pledge_product["pledge_shares"] == create_test_pledge_product.pledge_shares


def test_get_all_products_pledge_participant_sees_own_share(authorized_client, create_test_pledge_product, create_test_user1):
    res = authorized_client.get("/products")

    assert res.status_code == 200
    pledge_product = next(item for item in res.json() if item["id"] == create_test_pledge_product.id)
    assert pledge_product["pledge_shares"] == {create_test_user1.username: 30.0}


def test_get_all_products_unrelated_user_hides_pledge_shares(client, create_test_pledge_product, create_test_user3):
    token = create_access_token(payload={"id": create_test_user3.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.get("/products")

    assert res.status_code == 200
    pledge_product = next(item for item in res.json() if item["id"] == create_test_pledge_product.id)
    assert pledge_product["pledge_shares"] is not None


def test_get_my_products(authorized_client, test_products, create_test_user1):
    res = authorized_client.get("/products/my")
    assert res.status_code == 200
    result = res.json()
    my_products_count = len([p for p in test_products if p.owner_id == create_test_user1.id])
    assert len(result) == my_products_count


def test_get_product_by_name(authorized_client, test_products):
    search_term = "mouse"
    res = authorized_client.get(f"/products/{search_term}")
    assert res.status_code == 200
    result = res.json()
    for product in result:
        assert search_term.lower() in product['product_name'].lower()


def test_get_product_by_name_not_found(authorized_client, test_products):
    search_term = "nonexistent"
    res = authorized_client.get(f"/products/{search_term}")
    assert res.status_code == 404


def test_update_own_product(authorized_client, test_products, create_test_user1):
    my_product = next(p for p in test_products if p.owner_id == create_test_user1.id)
    data = {"amount": 30}
    res = authorized_client.patch(f"/products/{my_product.product_name}", json=data)
    assert res.status_code == 200
    assert res.json()['updated_data']['amount'] == data['amount']


def test_update_product_not_owner(authorized_client, test_products, create_test_user2):
    not_my_product = next(p for p in test_products if p.owner_id == create_test_user2.id)
    data = {"amount": 30}
    res = authorized_client.patch(f"/products/{not_my_product.product_name}", json=data)
    assert res.status_code == 403


def test_update_product_not_found(authorized_client):
    data = {"amount": 30}
    res = authorized_client.patch("/products/nonexistent", json=data)
    assert res.status_code == 404


def test_update_normal_product_cannot_add_pledge_shares(authorized_client, test_products, create_test_user1):
    my_product = next(p for p in test_products if p.owner_id == create_test_user1.id)
    res = authorized_client.patch(
        f"/products/{my_product.product_name}",
        json={"pledge_shares": {create_test_user1.username: 10.0}},
    )
    assert res.status_code == 409


def test_update_pledge_product_shares(client, create_test_pledge_product, create_test_user2, create_test_user1):
    shares = {create_test_user1.username: 40.0}
    product_name = create_test_pledge_product.product_name
    token = create_access_token(payload={"id": create_test_user2.id})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    res = client.patch(
        f"/products/{product_name}",
        json={"pledge_shares": shares},
    )
    assert res.status_code == 200
    assert res.json()["updated_data"]["pledge_shares"] == shares

    res = client.patch(
        f"/products/{product_name}",
        json={"pledge_shares": None},
    )
    assert res.status_code == 200
    assert res.json()["updated_data"]["pledge_shares"] is None


def test_delete_own_product(authorized_client, test_products, create_test_user1):
    my_product = next(p for p in test_products if p.owner_id == create_test_user1.id)
    res = authorized_client.delete(f"/products/{my_product.product_name}")
    assert res.status_code == 200


def test_delete_product_not_owner(authorized_client, test_products, create_test_user2):
    not_my_product = next(p for p in test_products if p.owner_id == create_test_user2.id)
    res = authorized_client.delete(f"/products/{not_my_product.product_name}")
    assert res.status_code == 403


def test_delete_product_not_found(authorized_client):
    res = authorized_client.delete("/products/nonexistent")
    assert res.status_code == 404 