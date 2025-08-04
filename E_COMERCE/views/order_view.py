from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from E_COMERCE.services import cart_service,order_service,productitem_service
from django.contrib.auth.mixins import LoginRequiredMixin
import json


class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = order_service.get_user_orders(request.user)
        print(orders)

        return render(request, 'enduser/order_list.html', {
            'orders': orders
        })    
    
    
class OrderCreateView(View):
    def get(self, request):
        user = request.user
        cart_items = cart_service.get_user_cart_items(user.id)
        total_price = sum(item['total_price'] for item in cart_items)
        savings = cart_service.calculate_total_savings(user.id)

        return render(request, 'enduser/order_summary.html', {
            'cart_items': cart_items,
            'price': total_price,
            'savings': savings,
            'user': user
        })

    def post(self, request):
        address = request.POST.get("address")
        if not address:
            return JsonResponse({'error': 'Address is required.'}, status=400)
        
        try:
            order = order_service.create_order_from_cart(request.user, address)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'success': True, 'order_id': order.id})




class DirectOrderView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        product_item = productitem_service.get_product_item_by_id(item_id)

        if not product_item:
            return render(request, "404.html", status=404)

        return render(request, 'enduser/order_summary_singly.html', {
            'product_item': product_item,
            'user': request.user
        })
    
    
    def post(self, request):
        data = json.loads(request.body)
        product_item_id = data.get("product_item_id")
        quantity = int(data.get("quantity", 1))
        size = int(data.get("size"))
        address = data.get("address")

        if not all([product_item_id, quantity, size, address]):
            return JsonResponse({'error': 'Missing fields'}, status=400)

        order = order_service.create_direct_order(request.user, product_item_id, quantity, size, address)
        return JsonResponse({'success': True, 'order_id': order.id})

    

class CartItemUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            size = int(data.get('size')) if 'size' in data else None
            color = int(data.get('color')) if 'color' in data else None

            cart_service.update_cart_item_singly(
                user=request.user,
                item_id=pk,
                quantity=quantity,
                size=size,
                color=color
            )
            return JsonResponse({'success': True})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class CartItemRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            cart_service.remove_cart_item(user=request.user, item_id=pk)
            return JsonResponse({'success': True})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)