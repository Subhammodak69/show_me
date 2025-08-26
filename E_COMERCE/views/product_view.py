from django.views import View
from django.shortcuts import render
from E_COMERCE.services import product_service,category_service,sub_category_service,productitem_service
from django.http import JsonResponse
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.constants.decorators import EnduserRequiredMixin
from E_COMERCE.models import ProductItem
from django.db.models import Q

class ProductDetailsView(View):
    def get(self,request,item_id):
        product_item_data = productitem_service.get_product_items_data(item_id)
        related_products_data = productitem_service.get_product_item_related_product_items(product_item_data['product_id'])

        return render(request, 'enduser/product_details.html',{'product_item_data':product_item_data,'related_products_data':related_products_data})
    
    
def category_product_search(request):
    query = request.GET.get("q", "").strip()
    productitems = []
    if query == "":
        productitems = []
        
    else:
        productitems = ProductItem.objects.filter(
            product__name__icontains=query,
            is_active=True
        )
    print(f"Found {productitems.count()} items")  # log result count

    results = [{
        "id": item.id,
        "product_name": item.product.name,
        "price": item.price,
        "photo_url": item.photo_url,
    } for item in productitems]

    return JsonResponse(results, safe=False)


class ProductListView(AdminRequiredMixin,View):
    def get(self, request):
        products = product_service.get_all_products()
        return render(request, 'admin/product/product_list.html', {'products': products})
    
   
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
      
    
class ProductToggleStatusView(EnduserRequiredMixin,View):
    def post(self, request, product_id):
        product = product_service.get_product_by_id(product_id)
        product.is_active = not product.is_active
        product.save()
        return JsonResponse({'is_active': product.is_active})