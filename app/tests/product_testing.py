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