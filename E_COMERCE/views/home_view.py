from collections import defaultdict
from django.views import View
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin,EnduserRequiredMixin
from django.contrib.auth import login
from E_COMERCE.services import user_service,poster_service,category_service,order_service,productitem_service
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

        # ----- Category Data -----
        all_categories = category_service.get_all_category()  # Already a list
        print("all categories", all_categories)
        categories = random.sample(all_categories, min(len(all_categories), 12))

        # ----- Poster Data -----
        posters_qs = poster_service.get_all_posters()  # QuerySet
        posters = list(posters_qs)  # Convert to list
        print("posters", posters)

        # ----- Product/Best Deals Data -----
        all_products_qs = productitem_service.get_active_products()  # QuerySet
        all_products = list(all_products_qs)  # Convert to list
        print("all_products", all_products)
        best_deals = random.sample(all_products, min(len(all_products), 8))  # Use min(), not max()

        return render(
            request,
            'enduser/home.html',
            {
                'user': user_data,
                'categories': categories,
                'posters': posters,
                'best_deals': best_deals
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



