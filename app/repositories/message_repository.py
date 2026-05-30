from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.database.models import Message

class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: Session):
        super().__init__(Message, db)

    def get_conversation_history(self, customer_id: str, limit: int = 20) -> List[Message]:
        """
        Fetch recent messages in chronological order for conversation memory.
        """
        # Fetch the most recent messages (newest first)
        recent_messages = self.db.query(Message).filter(
            Message.customer_id == customer_id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        # Reverse them to restore ascending chronological order (oldest to newest)
        recent_messages.reverse()
        return recent_messages

    def get_by_whatsapp_message_id(self, whatsapp_message_id: str) -> Optional[Message]:
        """
        Fetch a message by its unique WhatsApp message ID.
        """
        if not whatsapp_message_id:
            return None
        return self.db.query(Message).filter(
            Message.whatsapp_message_id == whatsapp_message_id
        ).first()

