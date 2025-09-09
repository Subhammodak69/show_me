from django.views import View
from E_COMERCE.constants.decorators import EnduserRequiredMixin
from E_COMERCE.services.payment_service import *
from django.shortcuts import render
from django.http import Http404,HttpResponseBadRequest
from django.http import JsonResponse
import json

class PaymentCreateView(EnduserRequiredMixin,View):
    def get(self, request, order_id):
        order = get_order_by_id(order_id)
        methods = get_payment_methods()
        banks = get_banks()
        if not order:
            raise Http404("Order not found or inactive.")
        return render(request, 'enduser/payment.html', {'order': order, 'methods':methods , 'banks':banks})
    
    def post(self, request,order_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

        payment = create_payment(request.user,data)
        if(payment):
            payment_status_update(payment)
            return JsonResponse({'success': True, 'message': 'Payment completed successfully'})
        else:
            JsonResponse({'success': False, 'message': 'Payment not Failed! '})
        