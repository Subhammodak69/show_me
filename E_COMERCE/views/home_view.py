from django.views import View
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.services import user_service,poster_service,order_service,productitem_service,category_service
import random


class HomeView(View):
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
        categories = category_service.get_categories()

        # ----- Poster Data -----
        posters_qs = poster_service.get_all_posters()
        posters = list(posters_qs)  # convert to list

        # ----- Product/Best Deals Data -----
        products_by_category = productitem_service.get_all_productitems_by_category()

        # Flatten for best deals or other logic if needed
        all_products = [item for products in products_by_category.values() for item in products]

        best_deals = random.sample(all_products, min(len(all_products), 10))

        shuffled_products = all_products[:]
        random.shuffle(shuffled_products)

        return render(
            request,
            'enduser/home.html',
            {
                'user': user_data,
                'categories': categories,
                'posters': posters,
                'best_deals': best_deals,
                'products_by_category': products_by_category.items(),  # pass for template grouping
            }
        )



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



