import hmac
import hashlib
from fastapi import APIRouter, Request, Response, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database.db import get_db
from app.agent.conversation_manager import ConversationManager
from app.whatsapp.sender import whatsapp_sender
from app.core.logger import logger

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])

def verify_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """
    Optional secure verification of Meta webhooks using application secret key.
    Disabled if APP_SECRET is not configured.
    """
    # Meta uses HMAC-SHA256 signature prefix 'sha256='
    if not signature_header or not signature_header.startswith("sha256="):
        return False
        
    app_secret = getattr(settings, "APP_SECRET", None)
    if not app_secret:
        # Skip validation if no secret is configured
        return True
        
    expected_signature = signature_header.split("sha256=")[1]
    mac = hmac.new(
        app_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    )
    return hmac.compare_digest(mac.hexdigest(), expected_signature)


@router.get("")
def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    challenge: str = Query(None, alias="hub.challenge"),
    verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    GET handshake endpoint required by Meta Developer portal to verify webhook domain ownership.
    """
    logger.info(f"Webhook GET verification requested. Mode: {mode}, Verify Token: {verify_token}")
    
    if mode == "subscribe" and verify_token == settings.VERIFY_TOKEN:
        logger.info("Webhook verification handshake successful!")
        return Response(content=challenge, media_type="text/plain")
        
    logger.warning("Webhook verification handshake failed due to invalid verify token.")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch"
    )


@router.post("")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    POST endpoint that receives WhatsApp message notifications and processes them in real time.
    """
    body_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    
    # Process signature if configured
    if getattr(settings, "APP_SECRET", None) and not verify_webhook_signature(body_bytes, signature):
        logger.warning("Received unauthorized webhook message. Signature verification failed.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature validation failed"
        )
        
    try:
        payload = await request.json()
    except Exception:
        logger.error("Failed to parse incoming webhook body as JSON.")
        return {"status": "error", "message": "Invalid JSON payload"}
        
    logger.info(f"Received webhook payload: {payload}")
    
    # Check if this is a standard message notification change event
    if payload.get("object") != "whatsapp_business_account":
        return {"status": "ignored"}
        
    entry_list = payload.get("entry", [])
    for entry in entry_list:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])
            
            if not messages:
                continue
                
            # Parse only the first incoming message block
            msg = messages[0]
            if msg.get("type") != "text":
                # Only support text messages initially
                logger.info(f"Skipping non-text message type '{msg.get('type')}' from {msg.get('from')}.")
                continue
                
            from_phone = msg.get("from")
            message_text = msg.get("text", {}).get("body", "")
            
            # Fetch profile name
            wa_name = "Customer"
            if contacts:
                wa_name = contacts[0].get("profile", {}).get("name", "Customer")
                
            logger.info(f"Message parsed: from={from_phone}, sender_name={wa_name}, body='{message_text}'")
            
            # Generate AI response
            try:
                ai_reply = ConversationManager.process_message(
                    db=db,
                    phone_number=from_phone,
                    user_name=wa_name,
                    message_content=message_text
                )
                
                # Send response back to the customer
                whatsapp_sender.send_text_message(to_phone=from_phone, text_body=ai_reply)
            except Exception as loop_err:
                logger.error(f"Error handling conversation loop: {str(loop_err)}")
                
    return {"status": "accepted"}
