from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.database.models import Customer

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def get_by_phone(self, phone_number: str) -> Optional[Customer]:
        """Fetch customer by unique phone number."""
        return self.db.query(Customer).filter(Customer.phone_number == phone_number).first()

    def get_or_create(self, phone_number: str, name: Optional[str] = None) -> Customer:
        """Fetch customer, or create a new profile if they don't exist yet."""
        customer = self.get_by_phone(phone_number)
        if not customer:
            customer = Customer(
                phone_number=phone_number,
                name=name or "Customer"
            )
            customer = self.create(customer)
        elif name and customer.name == "Customer":
            # Update default name if user provided a specific one
            customer.name = name
            self.update()
        return customer
