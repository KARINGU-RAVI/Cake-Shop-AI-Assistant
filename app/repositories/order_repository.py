from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.database.models import Order, OrderItem

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Fetch all orders placed by a specific customer."""
        return self.db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.created_at.desc()).all()

    def get_latest_pending_order(self, customer_id: str) -> Optional[Order]:
        """Fetch the most recent order that has not been confirmed or fully completed yet."""
        return self.db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.status == "PENDING"
        ).order_by(Order.created_at.desc()).first()

    def add_order_item(self, order_id: str, product_name: str, size: str, price: float, quantity: int = 1) -> OrderItem:
        """Appends a line item to an existing order."""
        item = OrderItem(
            order_id=order_id,
            product_name=product_name,
            size=size,
            price=price,
            quantity=quantity
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
