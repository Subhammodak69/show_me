from E_COMERCE.models import Payment,Order



def get_order_by_id(order_id):
    try:
        return Order.objects.get(id=order_id, is_active=True)
    except Order.DoesNotExist:
        return None

def create_payment(order, data):
    """
    data: dict from frontend.
    Must have at least transaction_reference (UPI ref/txn ID) and status (from PaymentStatus)
    """
    payment = Payment.objects.create(
        order=order,
        amount=order.total_price,
        status=data.get("status"),  # integer, use PaymentStatus enum
        transaction_reference=data.get("transaction_reference"),
        # add more fields as your model requires
    )
    return payment
