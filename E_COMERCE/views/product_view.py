from django.views import View
from django.shortcuts import render
from E_COMERCE.services import product_service,category_service,sub_category_service,productitem_service,rating_service
from django.http import JsonResponse
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.constants.decorators import EnduserRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class ProductDetailsView(View):
    def get(self,request,item_id):
        product_item_data = productitem_service.get_product_items_data(item_id)
        # print(product_item_data)
        related_products_data = productitem_service.get_product_item_related_product_items(product_item_data['id'])
        ratings_data = rating_service.get_all_ratings_by_product_item_id(item_id)
        return render(request, 'enduser/product_details.html',{'product_item_data':product_item_data,'related_products_data':related_products_data,'ratings': ratings_data})
    
    
class ProductListView(AdminRequiredMixin,View):
    def get(self, request):
        products = product_service.get_all_products()
        return render(request, 'admin/product/product_list.html', {'products': products})
    

@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(AdminRequiredMixin,View):
    def get(self, request):
        categories = category_service.get_categories()
        subcategories = sub_category_service.get_subcategories()
        return render(request, 'admin/product/product_create.html', {
            'categories': categories,
            'subcategories': subcategories
        })

    def post(self, request):
        try:
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'subcategory_id': request.POST.get('subcategory'),
            }
            product = product_service.create_product(data)
            return JsonResponse({'success': True, 'product_id': product.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class ProductUpdateView(AdminRequiredMixin,View):
    def get(self, request, product_id):
        product = product_service.get_product_object_by_id(product_id)
        categories = category_service.get_categories()
        subcategories = sub_category_service.get_subcategories()
        return render(request, 'admin/product/product_update.html', {
            'product': product,
            'categories': categories,
            'subcategories': subcategories
        })

    def post(self, request, product_id):
        try:
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'subcategory_id': request.POST.get('subcategory'),
            }
            product = product_service.update_product(product_id, data)
            return JsonResponse({'success': True, 'product_id': product.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
      

@method_decorator(csrf_exempt, name='dispatch')
class ProductToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, product_id):
        try:
            product = product_service.get_product_by_id(product_id)
            if not product:
                return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
            
            product.is_active = not product.is_active
            product.save()
            
            return JsonResponse({
                'success': True, 
                'new_status': product.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
