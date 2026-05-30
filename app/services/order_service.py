from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.database.models import Order
from app.database.seed import get_cake_price
from app.core.logger import logger

class OrderService:
    @staticmethod
    def calculate_total(flavor: str, size: str, quantity: int = 1, extra_charges: float = 0.0) -> float:
        """
        Calculate total price of a cake order including any extra custom options.
        """
        unit_price = get_cake_price(flavor, size)
        if unit_price == 0.0:
            logger.warning(f"Price not found for flavor '{flavor}' and size '{size}'. Defaulting to ₹500.")
            unit_price = 500.0  # Fallback standard cake price
            
        base_total = unit_price * quantity
        final_total = base_total + extra_charges
        logger.info(f"Calculated total: {quantity}x {flavor} ({size}) @ ₹{unit_price} each + ₹{extra_charges} custom fee = ₹{final_total}")
        return final_total

    @staticmethod
    def create_order(
        db: Session,
        phone_number: str,
        flavor: str,
        size: str,
        delivery_type: str,
        address: Optional[str] = None,
        delivery_date: Optional[str] = None,
        delivery_time: Optional[str] = None,
        name_on_cake: Optional[str] = None,
        message_on_cake: Optional[str] = None,
        quantity: int = 1,
        photo_cake: bool = False,
        eggless: bool = False,
        custom_extra_charges: float = 0.0
    ) -> Dict[str, Any]:
        """
        Processes order request, saves Customer, Order, and OrderItem to DB, and returns confirmation metadata.
        """
        cust_repo = CustomerRepository(db)
        order_repo = OrderRepository(db)
        
        customer = cust_repo.get_or_create(phone_number)
        
        # Calculate extra charges
        extra_charges = custom_extra_charges
        if photo_cake:
            extra_charges += 150.0  # Photo cake fee
        if eggless:
            extra_charges += 50.0   # Eggless surcharge
        if delivery_type.strip().upper() == "DELIVERY":
            extra_charges += 50.0   # Home delivery fee
            
        total_amount = OrderService.calculate_total(flavor, size, quantity, extra_charges)
        
        # Create fresh order
        order = Order(
            customer_id=customer.id,
            status="PENDING",
            delivery_type=delivery_type.upper(),
            address=address,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
            name_on_cake=name_on_cake,
            message_on_cake=message_on_cake,
            total_amount=total_amount
        )
        order = order_repo.create(order)
        
        # Add item details
        unit_price = get_cake_price(flavor, size)
        if unit_price == 0.0:
            unit_price = 500.0
        order_repo.add_order_item(
            order_id=order.id,
            product_name=flavor,
            size=size,
            price=unit_price,
            quantity=quantity
        )
        
        logger.info(f"Successfully created order {order.id} for customer phone {phone_number}.")
        return {
            "order_id": order.id,
            "total_amount": total_amount,
            "status": order.status,
            "delivery_type": order.delivery_type
        }

    @staticmethod
    def get_order_status(db: Session, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches an order's status and item details.
        """
        order_repo = OrderRepository(db)
        order = order_repo.get(order_id)
        if not order:
            return None
            
        items = []
        for item in order.items:
            items.append({
                "product_name": item.product_name,
                "size": item.size,
                "quantity": item.quantity,
                "price": item.price
            })
            
        return {
            "order_id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
            "delivery_type": order.delivery_type,
            "delivery_date": order.delivery_date,
            "delivery_time": order.delivery_time,
            "items": items
        }
