import json
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from E_COMERCE.constants.default_values import Size
from E_COMERCE.services import orderitem_service
from E_COMERCE.constants.decorators import AdminRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



#admin
class AdminOrderItemListView(AdminRequiredMixin, View):
    def get(self, request):
        items = orderitem_service.get_all_orderitems()
        return render(request, 'admin/orderitem/orderitem_list.html', {
            'orderitems': items
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdminOrderItemCreateView(AdminRequiredMixin, View):
    def get(self, request):
        product_items =  orderitem_service.get_all_product_items()
        return render(request, 'admin/orderitem/orderitem_create.html', {
            'orders': orderitem_service.get_all_orders(),
            'product_items':product_items,
            'sizes': [(s.value, s.name) for s in Size]
        })

    def post(self, request):
        data = {
            'order_id': request.POST.get('order_id'),
            'product_item': request.POST.get('product_item'),
            'quantity': request.POST.get('quantity'),
            'size': request.POST.get('size'),
            'is_active': request.POST.get('is_active') == 'on'
        }
        orderitem_service.create_orderitem(data)
        return redirect('admin_orderitem_list')


@method_decorator(csrf_exempt, name='dispatch')
class AdminOrderItemToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            body = json.loads(request.body)
            is_active = body.get('is_active')
            new_status = orderitem_service.toggle_orderitem_status(pk, is_active)
            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class AdminOrderItemUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        item = orderitem_service.get_orderitem_by_id(pk)
        return render(request, 'admin/orderitem/orderitem_update.html', {
            'orderitem': item,
            'orders': orderitem_service.get_all_orders(),
            'product_items': orderitem_service.get_all_product_items(),
            'sizes': [(s.value, s.name) for s in Size]
        })

    def post(self, request, pk):
        data = {
            'order_id': request.POST.get('order_id'),
            'product_item': request.POST.get('product_item'),
            'quantity': request.POST.get('quantity'),
            'size': request.POST.get('size'),
            'is_active': request.POST.get('is_active') == 'on'
        }
        orderitem_service.update_orderitem(pk, data)
        return redirect('admin_orderitem_list')
