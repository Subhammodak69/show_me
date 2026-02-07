from django.views import View
from django.shortcuts import render,redirect
from django.http import JsonResponse
from E_COMERCE.services import cart_service,order_service,product_info_service
from E_COMERCE.constants.decorators import EnduserRequiredMixin
import json
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.constants.default_values import Status
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



class OrderListView(EnduserRequiredMixin, View):    
    def get(self, request):
        orders = order_service.get_user_orders(request.user)        
        return render(request, 'enduser/order_list.html', {
            'orders': orders,
        })

  
    
@method_decorator(csrf_exempt, name='dispatch')
class OrderCreateView(EnduserRequiredMixin, View):
    def get(self, request):
        user = request.user
        cart_items = cart_service.get_user_cart_items(user.id)
        if not cart_items:
            return redirect('/cart/')
        
        # Calculate totals safely
        price = sum(item['total_price'] for item in cart_items)
        total_discount = sum(
            (item.get('discount') or 0) * item.get('quantity', 1) 
            for item in cart_items
        )
        total = price - total_discount

        return render(request, 'enduser/order_summary.html', {
            'cart_items': cart_items,
            'price': price,
            'discount': total_discount,
            'user': user,
            'total': total,
        })


    def post(self, request):
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        # print(address)
        # print(phone)
        if not address:
            return JsonResponse({'error': 'Delivery address is required.'}, status=400)
            
        if not phone:
            return JsonResponse({'error': 'Phone number is required.'}, status=400)
        
        try:
            order = order_service.create_order_from_cart(request.user, address, phone)
            return redirect(f'/track_order/{order.id}/')

            
        except ValueError as e:
            return redirect('/cart/')


@method_decorator(csrf_exempt, name='dispatch')
class DirectOrderView(EnduserRequiredMixin, View):
    def get(self, request):
        variant_id = request.GET.get('variant_id')
        # print(variant_id)
        item_data = product_info_service.get_item_data_by_varient(variant_id) 
        # print(item_data)
        if not item_data:
            return JsonResponse({'error': 'Product variant not found.'}, status=404)

        return render(request, 'enduser/order_summary_singly.html', {
            'item_data': item_data,
            'user': request.user
        })
    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # 🔥 Extract with proper defaults
        product_item_id = data.get("product_item_id")
        quantity = int(data.get("quantity", 1))
        size = int(data.get("size")) if data.get("size") else None
        color = int(data.get("color")) if data.get("color") else None  # 🔥 FIX: Handle null
        address = data.get("address")
        phone = data.get("phone")

        # 🔥 Specific field validation
        missing_fields = []
        if not product_item_id:
            missing_fields.append("product")
        if not quantity or quantity <= 0:
            missing_fields.append("quantity")
        if not size:
            missing_fields.append("size")
        if not address:
            missing_fields.append("address")
        if not phone:
            missing_fields.append("phone number")

        if missing_fields:
            return JsonResponse({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        try:
            # 🔥 ADD STOCK VALIDATION
            variant = product_info_service.get_iteminfo_by_product_item(
                product_item_id, size, color
            )
            if not variant:
                return JsonResponse({'error': 'Selected variant not found'})
            
            if variant.stock < quantity:
                return JsonResponse({
                    'error': f'Insufficient stock. Available: {variant.stock}'
                })

            # 🔥 Create order
            order = order_service.create_direct_order(
                request.user, variant.id, quantity, size, color, 
                address, phone
            )
            return JsonResponse({
            'success': True,
            'message': 'Order placed successfully!',
            'order_id': order.id
        })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SingleOrderUpdateView(EnduserRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_item_id = data.get('product_item_id')  # variant.product_item.id
            quantity = int(data.get('quantity', 1))
            size = int(data.get('size')) if data.get('size') else None
            color = int(data.get('color')) if data.get('color') else None

            # 🔥 Get variant with selected size/color
            variant = product_info_service.get_iteminfo_by_product_item(
                product_item_id, size, color
            )
            
            if not variant:
                return JsonResponse({
                    'success': False,
                    'error': 'Variant not found'
                })

            # 🔥 Stock validation
            if variant.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Insufficient stock (Available: {variant.stock})'
                })

            # 🔥 Calculate fresh summary
            original_price = variant.product_item.price * quantity
            discount = (cart_service.get_discount_by_id(variant.product_item) or 0) * quantity
            total = original_price - discount

            return JsonResponse({
                'success': True,
                'message': 'Order updated successfully',
                'summary': {
                    'original_price': float(original_price),
                    'discount': float(discount),
                    'total': float(total)
                }
            })

        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid data format'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

    
@method_decorator(csrf_exempt, name='dispatch')
class CartItemUpdateView(EnduserRequiredMixin, View):
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

@method_decorator(csrf_exempt, name='dispatch')
class CartItemRemoveView(EnduserRequiredMixin, View):
    def post(self, request, pk):
        try:
            cart_service.remove_cart_item(user=request.user, item_id=pk)
            return JsonResponse({'success': True})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)
        
        
@method_decorator(csrf_exempt, name='dispatch')    
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



#admin



class AdminOrderListView(AdminRequiredMixin,View):
    def get(self, request):
        orders = order_service.get_all_orders()
        return render(request, 'admin/order/order_list.html', {'orders': orders})

@method_decorator(csrf_exempt, name='dispatch')
class AdminOrderCreateView(AdminRequiredMixin,View):
    def get(self, request):
        users = order_service.get_all_users()
        return render(request, 'admin/order/order_create.html', {
            'users': users,
            'statuses': [(s.value, s.name) for s in Status]
        })

    def post(self, request):
        data = {
            'created_by': request.POST.get("created_by"),
            'phone': request.POST.get("phone"),
            'delivery_address': request.POST.get("delivery_address"),
            'status': request.POST.get("status"),
            'total_price': request.POST.get("total_price"),
            'is_active': request.POST.get("is_active") == "on",
        }
        order_service.create_order(data)
        return redirect("admin_order_list")

@method_decorator(csrf_exempt, name='dispatch')
class AdminOrderUpdateView(AdminRequiredMixin,View):
    def get(self, request, pk):
        order = order_service.get_order_by_id(pk)
        users = order_service.get_all_users()
        return render(request, 'admin/order/order_update.html', {
            'order': order,
            'users': users,
            'statuses': [(s.value, s.name) for s in Status]
        })

    def post(self, request, pk):
        data = {
            'created_by': request.POST.get("created_by"),
            'phone': request.POST.get("phone"),
            'delivery_address': request.POST.get("delivery_address"),
            'status': request.POST.get("status"),
            'total_price': request.POST.get("total_price"),
            'is_active': request.POST.get("is_active") == "on",
        }
        order_service.update_order(pk, data)
        return redirect("admin_order_list")
    
@method_decorator(csrf_exempt, name='dispatch')
class AdminOrderToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            body = json.loads(request.body)
            is_active = body.get('is_active')

            new_status = order_service.toggle_order_active_status(pk, is_active)

            return JsonResponse({'success': True, 'new_status': new_status})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception:
            return JsonResponse({'success': False, 'error': 'Something went wrong'})
        


#enduser

class TrackOrderView( EnduserRequiredMixin,View):
    def get(self, request, order_id):
        context = order_service.get_order_tracking_info(order_id)
        if not context:
            # order not found, send minimal context for template
            context = {'order': None}
        return render(request, 'enduser/track.html', context)