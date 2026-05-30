from typing import List
from google.genai import types
from sqlalchemy.orm import Session
from app.repositories.message_repository import MessageRepository
from app.database.models import Customer
from app.core.logger import logger

class MemoryManager:
    @staticmethod
    def get_conversation_history(db: Session, customer: Customer, current_message: str, limit: int = 15) -> List[types.Content]:
        """
        Retrieves recent message logs for the customer, normalizes them into 
        google-genai types.Content objects, and appends the current message if not already present.
        """
        msg_repo = MessageRepository(db)
        history = msg_repo.get_conversation_history(customer.id, limit=limit)
        
        contents = []
        for msg in history:
            role = "user" if msg.sender_type == "USER" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )
            
        # Append the current fresh message only if it is not already the last message in history
        if not contents or contents[-1].parts[0].text != current_message or contents[-1].role != "user":
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=current_message)]
                )
            )
        
        logger.info(f"Loaded {len(contents)} message history records for phone {customer.phone_number}.")
        return contents
