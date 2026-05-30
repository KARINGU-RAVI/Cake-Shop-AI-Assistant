import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.database.models import Payment
from app.core.logger import logger

class PaymentService:
    @staticmethod
    def generate_payment_link(db: Session, order_id: str) -> Dict[str, Any]:
        """
        Creates a new pending payment record for an order and generates a mock checkout URL.
        """
        order_repo = OrderRepository(db)
        payment_repo = PaymentRepository(db)
        
        order = order_repo.get(order_id)
        if not order:
            logger.error(f"Failed to generate payment link: Order {order_id} not found.")
            return {"error": "Order not found"}
            
        # Check if payment already exists
        existing_payment = payment_repo.get_by_order_id(order_id)
        if existing_payment:
            logger.info(f"Returning existing payment link for order {order_id}.")
            return {
                "payment_id": existing_payment.id,
                "amount": existing_payment.amount,
                "status": existing_payment.status,
                "payment_link": existing_payment.payment_link
            }
            
        transaction_ref = f"txn_{uuid.uuid4().hex[:12]}"
        payment_link = f"https://sandbox.checkout.thecakeshop.in/pay/{transaction_ref}"
        
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            status="PENDING",
            payment_link=payment_link,
            transaction_reference=transaction_ref
        )
        payment = payment_repo.create(payment)
        
        logger.info(f"Generated payment link {payment_link} for order {order_id}.")
        return {
            "payment_id": payment.id,
            "amount": payment.amount,
            "status": payment.status,
            "payment_link": payment_link
        }

    @staticmethod
    def confirm_payment(db: Session, order_id: str, success: bool = True) -> Optional[Dict[str, Any]]:
        """
        Simulates payment completion hook, updating payment and order records.
        """
        order_repo = OrderRepository(db)
        payment_repo = PaymentRepository(db)
        
        order = order_repo.get(order_id)
        payment = payment_repo.get_by_order_id(order_id)
        
        if not order or not payment:
            logger.error(f"Cannot confirm payment: Order or Payment record missing for ID {order_id}.")
            return None
            
        payment.status = "COMPLETED" if success else "FAILED"
        payment_repo.update()
        
        if success:
            order.status = "CONFIRMED"
            order_repo.update()
            logger.info(f"Payment confirmed for order {order_id}. Order state set to CONFIRMED.")
        else:
            logger.info(f"Payment failed for order {order_id}. Order state remains PENDING.")
            
        return {
            "order_id": order.id,
            "payment_status": payment.status,
            "order_status": order.status
        }
