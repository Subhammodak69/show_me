import json
from django.views import View
from django.http import JsonResponse, Http404
from django.shortcuts import render
from E_COMERCE.services import payment_service,order_service
from django.core.exceptions import ObjectDoesNotExist

class PaymentCreateView(View):
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
        

class PaymentDeleteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')

            if not order_id:
                return JsonResponse({'success': False, 'error': 'Order ID required'}, status=400)

            order_service.delete_order_and_items(order_id)

            return JsonResponse({'success': True, 'message': 'Order and its items deleted successfully.'})

        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)