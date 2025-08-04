from django.views import View
from django.shortcuts import render
from E_COMERCE.services import wishlist_service,user_service,product_service
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.core.exceptions import ObjectDoesNotExist
from E_COMERCE.constants.decorators import EnduserRequiredMixin,AdminRequiredMixin

class WishlistListView(View):
    def get(self,request):
        return 
    
    
class WishlistDetailsView(EnduserRequiredMixin,View):
    def get(self,request):
        user_id =request.user.id
        wishlist_items_data = wishlist_service.get_wishlist_items(user_id)
        return render(request,'enduser/wishlist.html',{'wishlist_items_data':wishlist_items_data})


class WishlistDeleteView(EnduserRequiredMixin,View):
    def post(self, request):
        data = json.loads(request.body)
        wishlist_item_id = data.get("wishlist_id")

        try:
            wishlist_service.delete_wishlist_item_by_id(wishlist_item_id)
            return JsonResponse({"success": True})
        except:
            return JsonResponse({"success": False, "error": "Item not found"}, status=404)

class WishlistCreateUpdateView(EnduserRequiredMixin,View):
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            item_id = data.get("item_id")
            print(item_id,"hvgvbvb")
            if not item_id:
                return JsonResponse({'status': 'error', 'message': 'Product item ID is required'}, status=400)

            status = wishlist_service.toggle_user_wishlist(request.user, item_id)
            return JsonResponse({'status': status})
        
        except ObjectDoesNotExist as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=404)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)
        

#admin


class AdminWishlistListView(View):
    def get(self, request):
        wishlist_data = wishlist_service.get_all_wishlists()
        return render(request, 'admin/wishlist/wishlist_list.html', {
            'wishlist_data': wishlist_data
        })



class AdminWishlistCreateView(AdminRequiredMixin,View):
    def get(self, request):
        users = user_service.get_all_user()
        product_items = product_service.get_all_product_items()
        return render(request, 'admin/wishlist/wishlist_create.html', {
            'users': users,
            'product_items': product_items
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
            wishlist = wishlist_service.create_wishlist(data)
            return JsonResponse({'message': 'Wishlist created successfully', 'id': wishlist.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class AdminWishlistUpdateView(AdminRequiredMixin,View):
    def get(self, request, pk):
        wishlist = wishlist_service.get_wishlist_by_id(pk)
        users = user_service.get_all_user()
        product_items = product_service.get_all_product_items()
        return render(request, 'admin/wishlist/wishlist_update.html', {
            'wishlist': wishlist,
            'users': users,
            'product_items': product_items
        })

    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            updated_wishlist = wishlist_service.update_wishlist(pk, data)
            return JsonResponse({'message': 'Wishlist updated successfully', 'id': updated_wishlist.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class AdminWishlistToggleStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            body = json.loads(request.body)
            is_active = body.get('is_active')
            new_status = wishlist_service.toggle_wishlist_status(pk, is_active)
            return JsonResponse({'success': True, 'new_status': new_status})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception:
            return JsonResponse({'success': False, 'error': 'Something went wrong'})
