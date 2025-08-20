from E_COMERCE.models import Payment,Order
from E_COMERCE.constants.default_values import PaymentStatus




def get_order_by_id(order_id):
    try:
        return Order.objects.get(id=order_id, is_active=True)
    except Order.DoesNotExist:
        return None

def create_payment(order, amount, razorpay_order_id):
    payment = Payment.objects.create(
        order=order,
        amount=amount,
        payment_gateway_order_id=razorpay_order_id,
        status=PaymentStatus.PENDING.value,
    )
    return payment

def update_payment_status(razorpay_order_id, status, transaction_reference=None, utr=None):
    payment = Payment.objects.get(payment_gateway_order_id=razorpay_order_id)
    payment.status = status
    if transaction_reference:
        payment.transaction_reference = transaction_reference
    if utr:
        payment.utr = utr
    payment.save()
    return payment

