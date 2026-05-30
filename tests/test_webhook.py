from app.config import settings

def test_webhook_handshake_success(client):
    response = client.get(
        "/api/v1/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test-challenge-123",
            "hub.verify_token": settings.VERIFY_TOKEN
        }
    )
    assert response.status_code == 200
    assert response.text == "test-challenge-123"


def test_webhook_handshake_unauthorized(client):
    response = client.get(
        "/api/v1/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test-challenge-123",
            "hub.verify_token": "wrong-token"
        }
    )
    assert response.status_code == 403


def test_webhook_post_ignored_type(client):
    # Sends a payload that is not 'whatsapp_business_account' to verify it skips it
    payload = {
        "object": "facebook_page",
        "entry": []
    }
    response = client.post("/api/v1/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}
