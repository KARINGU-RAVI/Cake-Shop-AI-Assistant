from app.database.seed import get_cake_price
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService

def test_cake_catalog_prices():
    # Test valid prices from seed
    assert get_cake_price("Chocolate Truffle Cake", "1kg") == 500.0
    assert get_cake_price("Vanilla Cream Cake", "2kg") == 850.0
    assert get_cake_price("Red Velvet Cake", "3kg") == 1700.0
    
    # Test normalization/case sensitivity
    assert get_cake_price("chocolate truffle cake", "2 kg") == 900.0
    
    # Test fallback
    assert get_cake_price("Unknown Cake", "1kg") == 0.0


def test_customer_creation(db_session):
    cust_repo = CustomerRepository(db_session)
    customer = cust_repo.get_or_create(phone_number="919999999999", name="Aman")
    
    assert customer.id is not None
    assert customer.name == "Aman"
    assert customer.phone_number == "919999999999"
    
    # Assert same customer retrieved on second get_or_create
    retrieved = cust_repo.get_or_create(phone_number="919999999999", name="IgnoredName")
    assert retrieved.id == customer.id
    assert retrieved.name == "Aman"


def test_order_creation_service(db_session):
    # Test full service layer order insertion
    order_data = OrderService.create_order(
        db=db_session,
        phone_number="918888888888",
        flavor="Black Forest Cake",
        size="2kg",
        delivery_type="DELIVERY",
        address="123 Sweet Lane",
        delivery_date="2026-06-01",
        delivery_time="17:00",
        name_on_cake="Riya",
        message_on_cake="Happy Birthday Riya"
    )
    
    assert order_data["order_id"] is not None
    # 2kg Black Forest = ₹1000 + Delivery Fee ₹50 = ₹1050
    assert order_data["total_amount"] == 1050.0
    assert order_data["status"] == "PENDING"
    
    # Fetch status using service layer
    status_info = OrderService.get_order_status(db_session, order_data["order_id"])
    assert status_info is not None
    assert status_info["status"] == "PENDING"
    assert len(status_info["items"]) == 1
    assert status_info["items"][0]["product_name"] == "Black Forest Cake"
    assert status_info["items"][0]["size"] == "2kg"
