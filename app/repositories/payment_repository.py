from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.database.models import Payment

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Fetch payment details linked to an order."""
        return self.db.query(Payment).filter(Payment.order_id == order_id).first()

    def get_by_reference(self, reference: str) -> Optional[Payment]:
        """Fetch payment record by mock transaction reference."""
        return self.db.query(Payment).filter(Payment.transaction_reference == reference).first()
