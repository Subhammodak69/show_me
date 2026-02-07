from django.views import View
from django.shortcuts import render,redirect
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.services import user_service,poster_service,order_service,productitem_service,category_service,product_service
import random
from E_COMERCE.constants.default_values import Role
from django.http import JsonResponse

class HomeView(View):
    def get(self, request):
        # ----- User Data -----

        if request.user.is_authenticated:
            user_id = request.user.id
            user = user_service.get_user(user_id)
            if user.role == Role.ADMIN.value:
                return redirect('/admin/')
            user_data = {
                'user_id': user_id,
                'is_authenticated': True,
                'name': f"{user.first_name} {user.last_name}",
                'pic': user.profile_photo_url,
            }
        else:
            user_data = {'is_authenticated': False}
        categories = category_service.get_categories()
        # ----- Poster Data -----
        posters_qs = poster_service.get_all_posters()
        posters = list(posters_qs)  # convert to list
        return render(
            request,
            'enduser/home.html',
            {
                'user': user_data,
                'categories': categories,
                'posters': posters,
            }
        )


import random
from django.http import JsonResponse
from django.views import View

class BestDealsAPIView(View):
    def get(self, request):
        print("🔥 BestDealsAPIView - TOP 10 ONLY")
        products_by_category = productitem_service.get_all_productitems_by_category()
        all_products = [item for products in products_by_category.values() for item in products]
        
        # Add ratings
        for item in all_products:
            ratings = productitem_service.get_all_rating_by_product(item.product)
            item.rating = productitem_service.get_average_rating(ratings)
            item.rating_count = len(ratings)
        
        # ✅ TOP 10 ONLY
        best_deals = random.sample(all_products, min(len(all_products), 10))
        print(f"✅ Best deals: EXACTLY 10 items")
        
        return JsonResponse({
            'best_deals': [self._serialize_item(item) for item in best_deals]
        })

    def _serialize_item(self, item):
        # ✅ FIX: Handle dict price correctly
        price_data = item.price
        if isinstance(price_data, dict):
            original_price = price_data.get('original_price', 0)
            sale_price = price_data.get('sale_price', 0)
        else:
            original_price = price_data.original_price
            sale_price = price_data.sale_price
            
        return {
            'id': item.id,
            'photo_url': item.photo_url,
            'title': item.product.name,
            'rating': getattr(item, 'rating', 0),
            'rating_count': getattr(item, 'rating_count', 0),
            'original_price': original_price,
            'sale_price': sale_price,
            'product_id': item.product.id
        }

class ProductsByCategoryAPIView(View):
    def get(self, request, page=1):
        print(f"📦 ProductsByCategoryAPIView - Page {page} (12 products)")
        PRODUCTS_PER_PAGE = 12
        
        products_by_category = productitem_service.get_all_productitems_by_category()
        all_products = [item for products in products_by_category.values() for item in products]
        
        # Add ratings
        for item in all_products:
            ratings = productitem_service.get_all_rating_by_product(item.product)
            item.rating = productitem_service.get_average_rating(ratings)
            item.rating_count = len(ratings)
        
        serialized_categories = []
        for category, products in products_by_category.items():
            start = (page - 1) * PRODUCTS_PER_PAGE
            end = start + PRODUCTS_PER_PAGE
            paginated_products = products[start:end]
            
            if paginated_products:
                serialized_categories.append({
                    'category_id': category.id,
                    'category_name': category.name,
                    'products': [self._serialize_item(item) for item in paginated_products],
                    'has_more': len(products) > end
                })
        
        print(f"✅ Loaded {len(serialized_categories)} categories")
        return JsonResponse({
            'categories': serialized_categories,
            'page': page,
            'has_more': len(all_products) > (page * PRODUCTS_PER_PAGE)
        })

    def _serialize_item(self, item):
        # ✅ SAME FIX: Handle dict price correctly
        price_data = item.price
        if isinstance(price_data, dict):
            original_price = price_data.get('original_price', 0)
            sale_price = price_data.get('sale_price', 0)
        else:
            original_price = price_data.original_price
            sale_price = price_data.sale_price
            
        return {
            'id': item.id,
            'photo_url': item.photo_url,
            'title': item.product.name,
            'rating': getattr(item, 'rating', 0),
            'rating_count': getattr(item, 'rating_count', 0),
            'original_price': original_price,
            'sale_price': sale_price,
            'product_id': item.product.id
        }



class ApiSearchListView(View):
    def get(self, request):
        res = product_service.category_product_search(request)
        return res 
    



class AdminHomeView(AdminRequiredMixin, View):
    def get(self, request):
        total_users = user_service.get_total_user_count()
        total_orders = order_service.get_total_order_count()
        
        # Simulated sales data (you can replace with real logic)
        sales = order_service.get_sales().count()
        total_product_items = productitem_service.get_all_productitems().count()
        total_is_not_active_items = productitem_service.get_total_is_not_active_items().count()
        store = (total_product_items)-(total_is_not_active_items)
        recent_orders = (
            order_service.get_recent_orders()
        )

        return render(request, 'admin/dashboard.html', {
            'user': request.user,
            'total_users': total_users,
            'total_orders': total_orders,
            'sales': sales,
            'store': store,
            'recent_orders': recent_orders
        })



