from django.views import View
from django.shortcuts import render, redirect
from E_COMERCE.services import cart_service,cartitem_service,productitem_service
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.constants.default_values import Size,Color


#admin
class AdminCartItemListView(AdminRequiredMixin,View):
    def get(self, request):
        cart_items = cartitem_service.get_cart_items()
        return render(request, 'admin/cartitem/cartitem_list.html', {'cartitem_data': cart_items})

class AdminCartItemCreateView(AdminRequiredMixin,View):
    def get(self, request):
        carts = cart_service.get_all_carts()
        product_items = productitem_service.get_product_items()
        sizes = [(s.value, s.name) for s in Size]
        colors = [(c.value, c.name) for c in Color]
        return render(request, 'admin/cartitem/cartitem_create.html', {
            'carts': carts,
            'product_items': product_items,
            'sizes': sizes,
            'colors': colors
        })

    def post(self, request):
        cart_id = request.POST.get("cart")
        product_item_id = request.POST.get("product_item")
        size = request.POST.get("size")
        color = request.POST.get("color")
        quantity = request.POST.get("quantity", 1)

        cartitem_service.cartitem_create(cart_id,product_item_id,size,color,quantity)
        return redirect('admin_cartitem_list')

class AdminCartItemUpdateView(AdminRequiredMixin,View):
    def get(self, request, pk):
        cart_item = cartitem_service.get_cart_item_object(pk)
        product_items = productitem_service.get_product_items()
        sizes = [(s.value, s.name) for s in Size]
        colors = [(c.value, c.name) for c in Color]
        return render(request, 'admin/cartitem/cartitem_update.html', {
            'cart_item': cart_item,
            'product_items': product_items,
            'sizes': sizes,
            'colors': colors
        })

    def post(self, request, pk):
        cart_item = cartitem_service.get_cart_item_object(pk)

        cart_item.product_item_id = request.POST.get("product_item")
        cart_item.size = request.POST.get("size")
        cart_item.color = request.POST.get("color")
        cart_item.quantity = request.POST.get("quantity", 1)
        cart_item.save()

        return redirect('admin_cartitem_list')
