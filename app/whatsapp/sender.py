import requests
from app.config import settings
from app.core.logger import logger

class WhatsAppSender:
    def __init__(self):
        self.phone_number_id = settings.PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_TOKEN
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        logger.info(f"Initialized WhatsAppSender with URL: {self.base_url}")

    def send_text_message(self, to_phone: str, text_body: str) -> bool:
        """
        Sends a plain text message to the specified recipient phone number.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Clean phone number (remove +, spaces, leading zeros if standard international)
        clean_phone = to_phone.strip().replace("+", "").replace(" ", "")
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "body": text_body
            }
        }
        
        try:
            logger.info(f"Sending WhatsApp message to {clean_phone}...")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                res_data = response.json()
                logger.info(f"WhatsApp message sent successfully. Message ID: {res_data.get('messages', [{}])[0].get('id')}")
                return True
            else:
                logger.error(f"WhatsApp send failed with code {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"HTTP request error sending WhatsApp message: {str(e)}")
            return False

whatsapp_sender = WhatsAppSender()
