from collections import defaultdict
from django.views import View
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin,EnduserRequiredMixin
from django.contrib.auth import login
from E_COMERCE.services import user_service, product_service,wishlist_service,category_service,order_service
import random

class HomeView(EnduserRequiredMixin, View):
    def get(self, request):
        # ----- User Data -----
        if request.user.is_authenticated:
            user_id = request.user.id
            user = user_service.get_user(user_id)

            user_data = {
                'user_id': user_id,
                'is_authenticated': True,
                'name': f"{user.first_name} {user.last_name}",
                'pic': user.profile_photo_url,
            }
        else:
            user_data = {'is_authenticated': False}

        # ----- Wishlist -----
        user_wishlist_items_ids = wishlist_service.wishlist_item_ids(request.user.id)

        # ----- Products, Categories -----
        products = product_service.get_all_product_items()  # List of ProductItem
        categories = category_service.get_categories()      # List of Category

        # ----- Categorize ProductItems Randomly -----
        categorized_items = defaultdict(list)

        for item in products:
            product = item['product']
            category = product.subcategory.category if product else None

            if category and product.is_active and item['is_active']:
                categorized_items[category.name].append(item)

        # Shuffle items in each category
        for cat_items in categorized_items.values():
            random.shuffle(cat_items)

        # Convert defaultdict to dict before passing to template
        return render(
            request,
            'enduser/products.html',
            {
                'user': user_data,
                'categories': categories,
                'categorized_products': dict(categorized_items),  # key: category name, value: list of ProductItem
                'user_wishlist_items_ids': user_wishlist_items_ids,
            }
        )



class AdminHomeView(AdminRequiredMixin, View):
    def get(self, request):
        total_users = user_service.get_total_user_count()
        total_orders = order_service.get_total_order_count()
        
        # Simulated sales data (you can replace with real logic)
        sales = 56789
        store = 12345

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



