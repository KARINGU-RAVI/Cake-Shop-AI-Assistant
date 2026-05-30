import datetime
from typing import Dict, Any, List, Optional
from app.database.db import SessionLocal
from app.database.seed import get_cake_catalog
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.core.logger import logger

def get_products() -> Dict[str, Any]:
    """
    Retrieves the entire product catalog, cake flavors, weights, and price list.
    Use this when a customer asks for the menu, flavors, prices, or what is available.
    """
    logger.info("Executing tool: get_products")
    return get_cake_catalog()

def search_products(flavor_query: str) -> List[str]:
    """
    Searches the product menu for a specific flavor query or keyword.
    
    Args:
        flavor_query: A text query searching for a cake flavor (e.g., 'chocolate', 'velvet').
    """
    logger.info(f"Executing tool: search_products for query '{flavor_query}'")
    catalog = get_cake_catalog()
    results = []
    for name in catalog.keys():
        if flavor_query.lower() in name.lower():
            results.append(name)
    return results

def calculate_total(flavor: str, size: str, quantity: int, extra_charges: float) -> float:
    """
    Calculates the exact total order value based on the cake flavor, size, quantity, and extra customization charges.
    
    Args:
        flavor: The flavor of the cake (e.g., 'Chocolate Cake').
        size: The weight of the cake (e.g., '1kg', '2kg', '3kg').
        quantity: The number of cakes ordered.
        extra_charges: Additional surcharges like photo cake charge (₹150), eggless cake charge (₹50), or delivery fee (₹50).
    """
    logger.info(f"Executing tool: calculate_total for {quantity}x {flavor} ({size}) + ₹{extra_charges}")
    return OrderService.calculate_total(flavor, size, quantity, extra_charges)

def create_order(
    phone_number: str,
    flavor: str,
    size: str,
    delivery_type: str,
    address: str,
    delivery_date: str,
    delivery_time: str,
    name_on_cake: str,
    message_on_cake: str,
    quantity: int,
    photo_cake: bool,
    eggless: bool,
    custom_extra_charges: float
) -> Dict[str, Any]:
    """
    Creates a new customer order and item records in the database.
    Use this only when the customer has confirmed their order summary details.
    
    Args:
        phone_number: The customer's active WhatsApp phone number.
        flavor: The cake flavor selected (e.g., 'Chocolate Cake').
        size: The weight of the cake (e.g., '1kg', '2kg', '3kg').
        delivery_type: Ordering option - must be either 'DELIVERY' or 'PICKUP'.
        address: The complete shipping address (pass empty string if PICKUP).
        delivery_date: The scheduled date for the delivery/pickup.
        delivery_time: The scheduled time for the delivery/pickup.
        name_on_cake: Name to write on the cake (pass empty string if none).
        message_on_cake: Text/greeting message to write on the cake (pass empty string if none).
        quantity: The quantity of cakes.
        photo_cake: Set to True if this is a custom photo cake (₹150 charge applies).
        eggless: Set to True if this is an eggless cake (₹50 charge applies).
        custom_extra_charges: Sum of extra costs for birthday accessories or combo options.
    """
    logger.info(f"Executing tool: create_order for phone {phone_number}, flavor {flavor}, size {size}, custom extra ₹{custom_extra_charges}.")
    with SessionLocal() as db:
        return OrderService.create_order(
            db=db,
            phone_number=phone_number,
            flavor=flavor,
            size=size,
            delivery_type=delivery_type,
            address=address,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
            name_on_cake=name_on_cake,
            message_on_cake=message_on_cake,
            quantity=quantity,
            photo_cake=photo_cake,
            eggless=eggless,
            custom_extra_charges=custom_extra_charges
        )

def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Queries the current completion status and details of an order from the database.
    
    Args:
        order_id: The unique order identifier uuid.
    """
    logger.info(f"Executing tool: get_order_status for ID {order_id}")
    with SessionLocal() as db:
        status_info = OrderService.get_order_status(db, order_id)
        if not status_info:
            return {"error": "Order not found"}
        return status_info

def generate_payment_link(order_id: str) -> Dict[str, Any]:
    """
    Generates a secure sandbox payment checkout link for a pending order.
    
    Args:
        order_id: The unique order identifier uuid.
    """
    logger.info(f"Executing tool: generate_payment_link for ID {order_id}")
    with SessionLocal() as db:
        return PaymentService.generate_payment_link(db, order_id)

def get_current_datetime() -> str:
    """
    Returns the current server date and time in ISO standard format.
    Use this to validate delivery schedules relative to today's date.
    """
    now = datetime.datetime.now()
    logger.info(f"Executing tool: get_current_datetime -> {now.isoformat()}")
    return now.strftime("%Y-%m-%d %H:%M:%S (Local Time)")

# Export tool list for Gemini client registration
ALL_AGENT_TOOLS = [
    get_products,
    search_products,
    calculate_total,
    create_order,
    get_order_status,
    generate_payment_link,
    get_current_datetime
]

# Dispatcher mapping for executing tool calls dynamically
TOOL_DISPATCH_MAP = {
    "get_products": get_products,
    "search_products": search_products,
    "calculate_total": calculate_total,
    "create_order": create_order,
    "get_order_status": get_order_status,
    "generate_payment_link": generate_payment_link,
    "get_current_datetime": get_current_datetime
}
