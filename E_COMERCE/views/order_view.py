from django.views import View
from django.shortcuts import render,redirect
from django.http import JsonResponse
from E_COMERCE.services import cart_service,order_service,productitem_service
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
  
    

class OrderCreateView(EnduserRequiredMixin,View):
    def get(self, request):
        user = request.user
        cart_items = cart_service.get_user_cart_items(user.id)
        price = sum(item['total_price'] for item in cart_items)
        total_discount = sum((item.get('discount') or 0) for item in cart_items) # NEW LINE
        total = price-total_discount

        return render(request, 'enduser/order_summary.html', {
            'cart_items': cart_items,
            'price': price,
            'discount': total_discount,  # UPDATED KEY
            'user': user,
            'total':total,
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




class DirectOrderView(EnduserRequiredMixin, View):
    def get(self, request, item_id):
        product_item = productitem_service.get_product_item_by_id(item_id)

        if not product_item:
            return render(request, "404.html", status=404)

        return render(request, 'enduser/order_summary_singly.html', {
            'product_item': product_item,
            'user': request.user
        })
    
    
    def post(self, request,item_id):
        data = json.loads(request.body)
        product_item_id = data.get("product_item_id")
        quantity = int(data.get("quantity", 1))
        size = int(data.get("size"))
        address = data.get("address")

        if not all([product_item_id, quantity, size, address]):
            return JsonResponse({'error': 'Missing fields'}, status=400)

        order = order_service.create_direct_order(request.user, product_item_id, quantity, size, address)
        return JsonResponse({'success': True, 'order_id': order.id})

    

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
            'delivery_address': request.POST.get("delivery_address"),
            'status': request.POST.get("status"),
            'total_price': request.POST.get("total_price"),
            'is_active': request.POST.get("is_active") == "on",
        }
        order_service.create_order(data)
        return redirect("admin_order_list")


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
            'delivery_address': request.POST.get("delivery_address"),
            'status': request.POST.get("status"),
            'total_price': request.POST.get("total_price"),
            'is_active': request.POST.get("is_active") == "on",
        }
        order_service.update_order(pk, data)
        return redirect("admin_order_list")
    

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