from django.shortcuts import render
from django.views import View
from  E_COMERCE.services import cart_service,user_service,cartitem_service,product_info_service
from E_COMERCE.constants.decorators import EnduserRequiredMixin,AdminRequiredMixin
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from E_COMERCE.services import CartItem
#admin
class AdminCartListView(AdminRequiredMixin, View):
    def get(self, request):
        cart_data = cart_service.get_all_carts_with_summary()
        return render(request, 'admin/cart/cart_list.html', {'cart_data': cart_data})


@method_decorator(csrf_exempt, name='dispatch')
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
        


@method_decorator(csrf_exempt, name='dispatch')
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
        

@method_decorator(csrf_exempt, name='dispatch')
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


from django.db import transaction

@method_decorator(csrf_exempt, name='dispatch')
class ApiCartUpdateView(EnduserRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            cart_item_id = data.get('cart_item_id')
            quantity = data.get('quantity')
            size = data.get('size') 
            color = data.get('color') 

            # Validate input
            if not cart_item_id or not quantity or quantity <= 0:
                return JsonResponse({'success': False, 'error': 'Invalid quantity or item ID'})

            quantity = int(quantity)

            # ✅ Get cart item AND validate user ownership
            cart_item = cartitem_service.get_cart_item_object(cart_item_id)
            if not cart_item or cart_item.cart.user != request.user:
                return JsonResponse({'success': False, 'error': 'Cart item not found'})

            # ✅ Get variant with size/color (already integers)
            variant = product_info_service.get_iteminfo_by_product_item(
                cart_item.product_item, size, color
            )
            
            if not variant or variant.stock < quantity:
                return JsonResponse({
                    'success': False, 
                    'error': f'Insufficient stock (Available: {variant.stock if variant else 0})'
                })

            # ✅ TRANSACTION ATOMIC - Ensures all changes succeed or rollback completely
            with transaction.atomic():
                # FIXED LOGIC: Handle existing_target properly
                if cart_item.size == size and cart_item.color == color:
                    # Same variant - just update quantity
                    cart_item.quantity = quantity
                    cart_item.save()
                    updated_item = cart_item
                    
                else:
                    # Different variant - check for conflicts
                    existing_target = CartItem.objects.select_for_update().filter(
                        cart=cart_item.cart,
                        product_item=cart_item.product_item,
                        size=size,
                        color=color,
                        is_active=True  # Only active items matter for unique constraint
                    ).exclude(id=cart_item.id).first()

                    if existing_target:
                        # Active item exists with target size/color - MERGE
                        existing_target.quantity += quantity
                        if existing_target.quantity > variant.stock:
                            raise ValueError(f'Insufficient stock after merge (Available: {variant.stock})')
                        existing_target.save()
                        # Deactivate current item instead of delete
                        cart_item.is_active = False
                        cart_item.save()
                        updated_item = existing_target
                        
                    else:
                        # Check for inactive item with target size/color
                        inactive_target = CartItem.objects.select_for_update().filter(
                            cart=cart_item.cart,
                            product_item=cart_item.product_item,
                            size=size,
                            color=color,
                            is_active=False
                        ).exclude(id=cart_item.id).first()

                        if inactive_target:
                            # Reactivate inactive item
                            inactive_target.is_active = True
                            inactive_target.quantity = quantity
                            inactive_target.save()
                            # Deactivate current item
                            cart_item.is_active = False
                            cart_item.save()
                            updated_item = inactive_target
                        else:
                            # No conflict - safe to update current item
                            cart_item.size = size
                            cart_item.color = color
                            cart_item.quantity = quantity
                            cart_item.save()
                            updated_item = cart_item

            # Get updated cart summary (only active items) - OUTSIDE transaction
            cart_items = cart_service.get_cart_details(request.user)
            original_price = float(sum(item['product_item'].price * item['quantity'] for item in cart_items))
            total_discount = float(sum(
                (cart_service.get_discount_by_id(item['product_item']) or 0) * item['quantity']
                for item in cart_items
            ))
            platform_fee = float(0)
            total = float(original_price - total_discount + platform_fee)

            return JsonResponse({
                'success': True, 
                'message': 'Cart updated successfully',
                'cart_item': {
                    'id': updated_item.id,
                    'quantity': updated_item.quantity,
                    'size': updated_item.size,
                    'color': updated_item.color,
                },
                'summary': {
                    'original_price': original_price,
                    'discount': total_discount,
                    'platform_fee': platform_fee,
                    'total': total
                }
            })

        except ValueError as ve:
            return JsonResponse({'success': False, 'error': str(ve)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

#enduser
class CartDetailsView(EnduserRequiredMixin, View):
    def get(self, request):
        cart_items = cart_service.get_cart_details(request.user)
        total_items = sum(item['quantity'] for item in cart_items)
        original_price = sum(item['product_item'].price * item['quantity'] for item in cart_items)

        # Calculate total discount from each item's discount multiplied by quantity
        total_discount = sum(
            (cart_service.get_discount_by_id(item['product_item']) or 0) * item['quantity']
            for item in cart_items
        )

        platform_fee = 0
        total = original_price - total_discount + platform_fee

        return render(request, 'enduser/cart.html', {
            'cart_items': cart_items,
            'total_items': total_items,
            'price': original_price,
            'discount': total_discount,
            'platform_fee': platform_fee,
            'total': total
        })


        
    
@method_decorator(csrf_exempt, name='dispatch')
class CartCreateView(EnduserRequiredMixin,View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            varient_id = data.get('varient_id')
            quantity = int(data.get('quantity', 1))

            item = cart_service.add_item_to_cart(user, varient_id, quantity)
            return JsonResponse({'status': 'success', 'message': 'Item added to cart', 'item_id': item.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class CartDeleteView(AdminRequiredMixin,View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            cart_item_id = data.get('cart_item_id')

            cart_service.delete_cart_item(user, cart_item_id)
            return JsonResponse({'status': 'success', 'message': 'Item deleted'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
