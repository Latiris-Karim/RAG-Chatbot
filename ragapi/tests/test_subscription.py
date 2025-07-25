from conftest import client, fake_auth_header

def test_create_customer_unauthorized():
    payload = {"email": "test@example.com"}
    response = client.post("/subscription/create-customer", headers=fake_auth_header(), json=payload)
    assert response.status_code == 404

def test_create_subscription_unauthorized():
    payload = {"priceId": "price_123"}
    response = client.post("/subscription/create-subscription", headers=fake_auth_header(), json=payload)
    assert response.status_code == 404

def test_cancel_subscription_unauthorized():
    payload = {"subscriptionId": "sub_123"}
    response = client.post("/subscription/cancel-subscription", headers=fake_auth_header(), json=payload)
    assert response.status_code == 404

def test_get_subscriptions_unauthorized():
    response = client.get("/subscription/subscriptions", headers=fake_auth_header())
    assert response.status_code == 404

# POST /webhook (no auth required)
def test_stripe_webhook():
    payload = {"type": "invoice.payment_succeeded", "data": {"object": {"id": "inv_123"}}}
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
