import json
from django.views import View
from django.shortcuts import render
from E_COMERCE.services import payment_service,order_service
from django.core.exceptions import ObjectDoesNotExist
import base64
from io import BytesIO
import qrcode
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from E_COMERCE.constants.decorators import EnduserRequiredMixin
import json, razorpay
from django.http import JsonResponse, HttpResponse, Http404
from E_COMERCE.constants.default_values import PaymentStatus



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class PaymentCreateView(EnduserRequiredMixin,View):
    def get(self, request, order_id):
        order = payment_service.get_order_by_id(order_id)
        if not order:
            raise Http404("Order not found or inactive.")
        return render(request, 'enduser/payment.html', {'order': order})

    def post(self, request, order_id):
        try:
            order = payment_service.get_order_by_id(order_id)
            if not order:
                return JsonResponse({"error": "Order not found or inactive."}, status=404)

            data = json.loads(request.body)
            amount = data.get('amount')
            upi_id = data.get('upi_id')   # This line is important
            if not amount or not upi_id:
                return JsonResponse({"error": "Amount and UPI ID required"}, status=400)

            # Razorpay order creation (ensure valid credentials and required params)
            razorpay_order = razorpay_client.order.create({
                "amount": int(float(amount) * 100),
                "currency": "INR",
                "payment_capture": 1,
                # You may optionally add notes or metadata
            })

            payment = payment_service.create_payment(order, amount, razorpay_order['id'])
            # Optionally store upi_id in the Payment object or logs, if business-legal/safe
            return JsonResponse({
                "message": "Payment initiated!",
                "payment_id": payment.id,
                "razorpay_order_id": razorpay_order['id'],
                "amount": amount,
            })
        except Exception as e:
            print("Error in payment POST:", str(e))  # Add this for easier debugging
            return JsonResponse({"error": str(e)}, status=400)


from urllib.parse import quote  # For URL encoding

def generate_upi_qr(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            upi_id = data.get("upi_id", "")            # Used as payer name
            amount = data.get("amount")
            order_id = data.get("order_id", "")
            # You can validate upi_id here if you want (e.g., regex), or just use as name

            # Validation: require a real amount and a valid receiver UPI
            if not amount:
                return JsonResponse({"error": "Amount is required"}, status=400)
            
            receiver_upi_id = getattr(settings, "MERCHANT_UPI_ID", None)
            if not receiver_upi_id:
                return JsonResponse({"error": "No receiver UPI ID configured"}, status=500)
            
            # UPI expects all parameter values URL-encoded!
            pa = quote(str(receiver_upi_id))
            pn = quote(str(upi_id)) if upi_id else "Valued%20Customer"
            am = quote(str(amount))
            cu = "INR"
            tn = quote(f"Order {order_id}") if order_id else ""

            upi_url = f"upi://pay?pa={pa}&pn={pn}&am={am}&cu={cu}"
            if tn:
                upi_url += f"&tn={tn}"

            # Generate QR code:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(upi_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

            # (Optional) Log for debugging -- remove in production
            print("Generated UPI URL:", upi_url)

            return JsonResponse({"qr_code": qr_base64, "upi_url": upi_url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


from E_COMERCE.models import Payment

def payment_status(request):
    razorpay_order_id = request.GET.get("razorpay_order_id")
    if not razorpay_order_id:
        return JsonResponse({"error": "Missing order id"}, status=400)
    try:
        payment = Payment.objects.get(payment_gateway_order_id=razorpay_order_id)
        if payment.status == PaymentStatus.SUCCESS.value:
            status = "SUCCESS"
        elif payment.status == PaymentStatus.FAILED.value:
            status = "FAILED"
        else:
            status = "PENDING"
        return JsonResponse({"status": status})
    except Payment.DoesNotExist:
        return JsonResponse({"error": "No such payment"}, status=404)



@csrf_exempt
def razorpay_webhook(request):
    try:
        payload = json.loads(request.body)
        # Validate webhook with signature (recommended: see Razorpay docs)
        payment_entity = payload['payload']['payment']['entity']
        razorpay_order_id = payment_entity.get('order_id')
        status = payment_entity.get('status') # 'captured', 'failed', etc.
        transaction_reference = payment_entity.get('id')
        utr = payment_entity.get('acquirer_data', {}).get('upi_transaction_id')

        # Map Razorpay status to your PaymentStatus enum
        if status == "captured":
            payment_status = PaymentStatus.SUCCESS.value
        elif status == "failed":
            payment_status = PaymentStatus.FAILED.value
        else:
            payment_status = PaymentStatus.PENDING.value

        payment_service.update_payment_status(
            razorpay_order_id, payment_status, transaction_reference, utr
        )
    except Exception as e:
        return HttpResponse(str(e), status=400)
    return HttpResponse("OK", status=200)

        
        
class OrderDeleteView(EnduserRequiredMixin, View):
    def post(self, request, order_id):
        try:
            if not order_id:
                return JsonResponse({'success': False, 'error': 'Order ID required'}, status=400)

            order_service.delete_order_and_items(order_id)

            return JsonResponse({
                'success': True,
                'message': 'Order and its items deleted successfully.'
            })

        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
