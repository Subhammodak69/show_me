from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.services import productitem_service,wishlist_service
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class CategoryProductsListView(View):
    def get(self, request, category_id):  # Fix: self -> self
        page = request.GET.get('page', 1)
        product_items = productitem_service.get_product_items_by_category_paginated(category_id, int(page))
        
        if request.headers.get('HX-Request'):  # HTMX/AJAX request
            return render(request, 'enduser/partials/product_list_partial.html', {
                'product_items': product_items['items'],
                'has_next': product_items['has_next'],
                'next_page': product_items['next_page'],
                'category_id': category_id
            })
        
        # Initial page load
        user_wishlist_items_ids = wishlist_service.wishlist_item_ids(request.user.id)
        return render(request, 'enduser/products.html', {
            'product_items': product_items['items'],
            'initial_data': product_items,  # Pass pagination info
            'category_id': category_id,
            'user_wishlist_items_ids': user_wishlist_items_ids
        })

# ADD this new AJAX-only view
class CategoryProductsAjaxView(View):
    def get(self, request, category_id):
        page = request.GET.get('page', 1)
        product_items = productitem_service.get_product_items_by_category_paginated(category_id, int(page))
        return render(request, 'enduser/partials/product_list_partial.html', {
            'product_items': product_items['items'],
            'has_next': product_items['has_next'],
            'next_page': product_items['next_page'],
            'category_id': category_id
        })

class ProductItemListView(AdminRequiredMixin, View):

    def get(self, request):
        products = productitem_service.get_all_productitems()
        return render(request, 'admin/productitem/productitem_list.html', {'productitems': products})


@method_decorator(csrf_exempt, name='dispatch')
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



@method_decorator(csrf_exempt, name='dispatch')
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
        

@method_decorator(csrf_exempt, name='dispatch')
class ProductItemToggleStatusView(AdminRequiredMixin, View):

    def post(self, request, productitem_id):
        try:
            new_status = productitem_service.toggle_productitem_status(productitem_id)
            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})