from django.shortcuts import render
from django.views import View
from  E_COMERCE.services import cart_service,user_service
from E_COMERCE.constants.decorators import EnduserRequiredMixin,AdminRequiredMixin
import json
from django.http import JsonResponse

#admin
class AdminCartListView(AdminRequiredMixin, View):
    def get(self, request):
        cart_data = cart_service.get_all_carts_with_summary()
        return render(request, 'admin/cart/cart_list.html', {'cart_data': cart_data})


class AdminCartToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, cart_id):
        try:
            body = json.loads(request.body)
            is_active = body.get('is_active')
            new_status = cart_service.toggle_cart_status_by_id(cart_id, is_active)
            return JsonResponse({'success': True, 'new_status': new_status})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception:
            return JsonResponse({'success': False, 'error': 'Something went wrong'})
        

class AdminCartCreateView(AdminRequiredMixin, View):
    def get(self, request):
        users = user_service.get_all_user()
        return render(request, 'admin/cart/cart_create.html',{'users':users})

    def post(self, request):
        try:
            data = json.loads(request.body)
            cart = cart_service.create_cart(data, request.user)
            return JsonResponse({'message': 'Cart created successfully!', 'id': cart.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        


class AdminCartUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        cart = cart_service.get_cart_by_id(pk)
        users = user_service.get_all_user()
        return render(request, 'admin/cart/cart_update.html', {
            'cart': cart,
            'users': users
        })

    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            updated_cart = cart_service.update_cart(pk, data)
            return JsonResponse({'message': 'Cart updated successfully!', 'id': updated_cart.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

#enduser

class CartDetailsView(EnduserRequiredMixin, View):
    def get(self, request):
        cart_items = cart_service.get_cart_details(request.user)
        print(cart_items)

        total_items = len(cart_items)
        original_price = sum(item['product_item'].price for item in cart_items)
        discount = round(original_price * 0.25) if original_price else 0
        platform_fee = 4 if original_price else 0
        total = original_price - discount + platform_fee

        return render(request, 'enduser/cart.html', {
            'cart_items': cart_items,
            'total_items': total_items,
            'price': original_price,
            'discount': discount,
            'platform_fee': platform_fee,
            'total': total
        })

        
    

class CartCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            product_item_id = data.get('product_item_id')
            size = data.get('size')
            color = data.get('color')
            quantity = int(data.get('quantity', 1))

            item = cart_service.add_item_to_cart(user, product_item_id, size, color, quantity)
            return JsonResponse({'status': 'success', 'message': 'Item added to cart', 'item_id': item.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class CartUpdateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            cart_item_id = data.get('cart_item_id')
            quantity = int(data.get('quantity'))

            item = cart_service.update_cart_item(user, cart_item_id, quantity)
            return JsonResponse({'status': 'success', 'message': 'Item updated', 'item_id': item.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class CartDeleteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            cart_item_id = data.get('cart_item_id')

            cart_service.delete_cart_item(user, cart_item_id)
            return JsonResponse({'status': 'success', 'message': 'Item deleted'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
