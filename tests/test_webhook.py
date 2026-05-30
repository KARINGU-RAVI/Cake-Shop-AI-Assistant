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


def test_webhook_deduplication(client, db_session):
    from unittest.mock import patch
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "1106816779186262",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15556529069",
                        "phone_number_id": "1046386211902187"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Arjun"
                        },
                        "wa_id": "919999999999"
                    }],
                    "messages": [{
                        "from": "919999999999",
                        "id": "wamid.HBgMOTE5MTgyMjA0NDAwFQIAEhggQUM3NTg2NUU4N0NDNTBFMUVC",
                        "timestamp": "1665096537",
                        "text": {
                            "body": "Hello Shop!"
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    with patch("app.agent.conversation_manager.ConversationManager.process_message") as mock_process, \
         patch("app.whatsapp.sender.whatsapp_sender.send_text_message") as mock_send:
         
        mock_process.return_value = "Mock response"
        mock_send.return_value = True
        
        # First request
        response1 = client.post("/api/v1/webhook", json=payload)
        assert response1.status_code == 200
        assert response1.json() == {"status": "accepted"}
        
        # Manually save the message to simulate it was successfully processed and saved
        from app.database.models import Message
        from app.repositories.customer_repository import CustomerRepository
        cust_repo = CustomerRepository(db_session)
        customer = cust_repo.get_or_create(phone_number="919999999999", name="Arjun")
        user_msg = Message(
            customer_id=customer.id,
            sender_type="USER",
            content="Hello Shop!",
            whatsapp_message_id="wamid.HBgMOTE5MTgyMjA0NDAwFQIAEhggQUM3NTg2NUU4N0NDNTBFMUVC"
        )
        db_session.add(user_msg)
        db_session.commit()
        
        # Second request (duplicate wamid)
        response2 = client.post("/api/v1/webhook", json=payload)
        assert response2.status_code == 200
        assert response2.json() == {"status": "accepted"}
        
        # Verify that process_message and send_text_message were called exactly ONCE
        assert mock_process.call_count == 1
        assert mock_send.call_count == 1


def test_chronological_history_retrieval(db_session):
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.message_repository import MessageRepository
    from app.database.models import Message
    
    cust_repo = CustomerRepository(db_session)
    msg_repo = MessageRepository(db_session)
    
    customer = cust_repo.get_or_create(phone_number="919999999999", name="Aman")
    
    import datetime
    # Insert 5 messages sequentially with distinct timestamps
    base_time = datetime.datetime.utcnow()
    for i in range(5):
        msg = Message(
            customer_id=customer.id,
            sender_type="USER",
            content=f"Message {i}",
            timestamp=base_time + datetime.timedelta(seconds=i)
        )
        msg_repo.create(msg)
        
    # Query with limit=3
    history = msg_repo.get_conversation_history(customer.id, limit=3)
    
    # Assert we get exactly 3 messages
    assert len(history) == 3
    
    # Assert they are the most recent ones (Message 2, Message 3, Message 4)
    # in ascending chronological order (2 -> 3 -> 4)
    assert history[0].content == "Message 2"
    assert history[1].content == "Message 3"
    assert history[2].content == "Message 4"

