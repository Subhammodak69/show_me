from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from E_COMERCE.constants.decorators import AdminRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from E_COMERCE.services.offer_service import (
    get_all_offers,
    get_offer_by_id,
    create_offer,
    update_offer,
    toggle_offer_status,
    get_all_products,
)
import json

class OfferListView(AdminRequiredMixin,View):
    def get(self, request):
        offers = get_all_offers()
        context = {'offers': offers}
        return render(request, 'admin/offer/offer_list.html', context)

class OfferCreateView(AdminRequiredMixin,View):
    def get(self, request):
        context = {'products': get_all_products()}
        return render(request, 'admin/offer/offer_create.html', context)

    def post(self, request):
        data = request.POST.copy()
        # Convert POSTed start_date and end_date to appropriate datetime objects if needed
        try:
            offer_data = {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'product_id': data.get('product') if data.get('product') else None,
                'discount_value': data.get('discount_value'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
            }
            # Remove keys with None values (optional)
            offer_data = {k: v for k, v in offer_data.items() if v is not None}
            offer = create_offer(offer_data)
            return JsonResponse({'success': True, 'id': offer.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class OfferUpdateView(AdminRequiredMixin,View):
    def get(self, request, pk):
        offer = get_offer_by_id(pk)
        if not offer:
            return redirect('offer_list')
        context = {'offer': offer, 'products': get_all_products()}
        return render(request, 'admin/offer/offer_update.html', context)

    def post(self, request, pk):
        offer = get_offer_by_id(pk)
        if not offer:
            return JsonResponse({'success': False, 'error': 'Offer not found'})
        data = request.POST.copy()
        try:
            update_data = {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'product_id': data.get('product') if data.get('product') else None,
                'discount_value': data.get('discount_value'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
            }
            update_data = {k: v for k, v in update_data.items() if v is not None}
            update_offer(offer, update_data)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class OfferToggleStatusView(AdminRequiredMixin,View):
    def post(self, request, pk):
        offer = get_offer_by_id(pk)
        if not offer:
            return JsonResponse({'success': False, 'error': 'Offer not found'})
        try:
            body = json.loads(request.body)
            new_status = body.get('is_active', True)
            result = toggle_offer_status(offer, new_status)
            return JsonResponse({'success': True, 'new_status': result})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
