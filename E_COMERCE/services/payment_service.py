from E_COMERCE.models import Payment,Order
from django.http import JsonResponse
from E_COMERCE.constants.default_values import PayMethods,PaymentStatus,Banks,Status


def get_order_by_id(order_id):
    try:
        return Order.objects.get(id=order_id, is_active=True)
    except Order.DoesNotExist:
        return None

def create_payment(user,data):
    method = data.get('method')
    amount = data.get('amount')
    order_id = data.get('order_id')

    if not (method and amount and order_id):
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

    # Validate order existence (assuming active orders only)
    try:
        order = Order.objects.get(id=order_id, is_active=True)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found or inactive'}, status=404)

    # Collect optional payment details based on method
    card_number = data.get('cardNumber') if method == 'card' else None
    expiry_date = data.get('expiry') if method == 'card' else None
    upi_id = data.get('upiId') if method == 'upi' else None
    bank = data.get('bank') if method == 'netbanking' else None

    # Create Payment record (in real app, integrate payment gateway here)
    return Payment.objects.create(
        user=user,
        amount=amount,
        method=method,
        status=PaymentStatus.PENDING.value,
        card_number=card_number,
        expiry_date=expiry_date,
        upi_id=upi_id,
        bank=bank,
    )
    
    
    
def payment_status_update(payment,order_id):
    order_obj = Order.objects.get(id=order_id,is_active=True)
    order_obj.status = Status.PROCESSING.value
    order_obj.save()
    
    payment_obj = Payment.objects.get(id=payment.id)
    payment_obj.status = PaymentStatus.SUCCESS.value
    payment_obj.save() 
    return 

def get_payment_methods():
    data = [
        {
            'name':m.name,
            'value':m.value
        }
        for m in PayMethods
    ]
    return data

def  get_banks():
    data = [
        {
            'name':b.name,
            'value':b.value
        }
        for b in Banks        
    ]
    return data