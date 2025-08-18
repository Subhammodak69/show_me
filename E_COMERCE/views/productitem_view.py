from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.services import productitem_service,wishlist_service


class CategoryProductsListView(View):
    def get(sel,request,category_id):
        product_items = productitem_service.get_product_items_by_category(category_id)
        user_wishlist_items_ids = wishlist_service.wishlist_item_ids(request.user.id)
        return render(request,'enduser/products.html',{'product_items':product_items,'user_wishlist_items_ids':user_wishlist_items_ids})


class ProductItemListView(AdminRequiredMixin, View):

    def get(self, request):
        products = productitem_service.get_all_productitems()
        return render(request, 'admin/productitem/productitem_list.html', {'productitems': products})


class ProductItemCreateView(AdminRequiredMixin, View):
    def get(self, request):
        products = productitem_service.get_active_products()
        sizes = productitem_service.get_size_choices_dict()
        colours = productitem_service.get_colour_choices_dict()
        return render(request, 'admin/productitem/productitem_create.html', {
            'products': products,
            'sizes': sizes,
            'colours': colours,
        })

    def post(self, request):
        try:
            file = request.FILES.get('photo')
            if not file:
                return JsonResponse({'success': False, 'error': 'Photo file is missing.'}, status=400)

            item = productitem_service.create_productitem(request, file)
            return JsonResponse({'success': True, 'id': item.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)




class ProductItemUpdateView(AdminRequiredMixin, View):

    def get(self, request, productitem_id):
        item = productitem_service.get_productitem_object(productitem_id)
        products = productitem_service.get_active_products()
        sizes = productitem_service.get_size_choices_dict()
        colours = productitem_service.get_colour_choices_dict()
        return render(request, 'admin/productitem/productitem_update.html', {
            'item': item,
            'products': products,
            'sizes': sizes,
            'colours':colours,
        })

    def post(self, request, productitem_id):
        try:
            data = request.POST
            file = request.FILES.get('photo')  # Optional
            productitem_service.update_productitem(productitem_id, data, file)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

class ProductItemToggleStatusView(AdminRequiredMixin, View):

    def post(self, request, productitem_id):
        try:
            new_status = productitem_service.toggle_productitem_status(productitem_id)
            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})