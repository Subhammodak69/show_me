import json
from django.views import View
from django.http import JsonResponse, Http404
from django.shortcuts import render
from E_COMERCE.services import payment_service,order_service
from django.core.exceptions import ObjectDoesNotExist
import base64
from io import BytesIO
import qrcode
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from E_COMERCE.constants.decorators import EnduserRequiredMixin


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
            # Frontend should send at least {status, transaction_reference}
            payment = payment_service.create_payment(order, data)
            return JsonResponse({
                "message": "Payment created successfully!",
                "payment_id": payment.id,
                "status": payment.status,
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        
class OrderDeleteView(EnduserRequiredMixin, View):
    def post(self, request, order_id):
        try:
            print("dsbhvdsh")
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


def generate_upi_qr(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            sender_upi_id = data.get("upi_id")  # This is the sender (customer)
            amount = data.get("amount")

            if not sender_upi_id or not amount:
                return JsonResponse({"error": "Sender UPI ID and amount are required"}, status=400)

            # Receiver is fixed from settings
            receiver_upi_id = settings.MERCHANT_UPI_ID

            # UPI payment URL format: receiver is `pa`, sender is in `pn` (payer name field)
            upi_url = f"upi://pay?pa={receiver_upi_id}&pn={sender_upi_id}&am={amount}&cu=INR"

            # Generate QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(upi_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64 for sending in JSON
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

            return JsonResponse({"qr_code": qr_base64})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
