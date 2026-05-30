from typing import List
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
        return self.db.query(Message).filter(
            Message.customer_id == customer_id
        ).order_by(Message.timestamp.asc()).limit(limit).all()
