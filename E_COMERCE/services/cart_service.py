from E_COMERCE.models import Cart, CartItem, ProductItem,User
from django.shortcuts import get_object_or_404
from E_COMERCE.constants.default_values import Size, Color

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, defaults={"is_active": True})
    return cart
from E_COMERCE.constants.default_values import Size, Color

def get_cart_details(user):
    cart = Cart.objects.filter(user=user, is_active=True).first()
    
    if not cart:
        return []

    cart_items_data = [
        {
            'id':item.id,
            'product_item': item.product_item,
            'quantity': item.quantity,
            'size': item.size,
            'color': item.color,
            'display_size': Size(item.size).name,
            'display_color': Color(item.color).name
        }
        for item in cart.items.filter(is_active=True).select_related('product_item')
    ]
    
    return cart_items_data


def add_item_to_cart(user, product_item_id, size, color, quantity):
    cart = get_or_create_cart(user)
    product_item = get_object_or_404(ProductItem, id=product_item_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_item=product_item,
        size=size,
        defaults={'quantity': quantity, 'color': color}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return item

def update_cart_item(user, cart_item_id, quantity):
    cart = get_or_create_cart(user)
    item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    item.quantity = quantity
    item.save()
    return item

def update_cart_item_singly(user, item_id, quantity=None, size=None, color=None):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=user, is_active=True)

        if quantity is not None:
            cart_item.quantity = quantity
        if size is not None:
            cart_item.size = size
        if color is not None:
            cart_item.color = color

        cart_item.save()
        return cart_item

    except CartItem.DoesNotExist:
        raise ValueError("Cart item not found")


def remove_cart_item(user, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=user, is_active=True)
        cart_item.is_active = False
        cart_item.save()
        return True
    except CartItem.DoesNotExist:
        raise ValueError("Cart item not found")




def delete_cart_item(user, cart_item_id):
    cart = get_or_create_cart(user)
    item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    item.delete()
    return True





#admin
def get_all_carts_with_summary():
    return Cart.objects.select_related('user').all()


def toggle_cart_status_by_id(cart_id, is_active=None):
    """
    Toggles the cart's is_active flag, or sets it directly if provided.
    """
    try:
        cart = Cart.objects.get(id=cart_id)
        cart.is_active = is_active if is_active is not None else not cart.is_active
        cart.save()
        return cart.is_active
    except Cart.DoesNotExist:
        raise ValueError("Cart not found.")
    
def create_cart(data, user):
    user_id = data.get("user_id")
    if not user_id:
        raise ValueError("User ID is required")

    selected_user = User.objects.get(id=user_id)

    # Optional: prevent duplicate cart
    if Cart.objects.filter(user=selected_user).exists():
        raise ValueError("A cart for this user already exists.")

    cart = Cart.objects.create(
        user=selected_user,
        is_active=data.get("is_active", True)
    )
    return cart


def get_cart_by_id(cart_id):
    return get_object_or_404(Cart, id=cart_id)

def update_cart(cart_id, data):
    cart = get_cart_by_id(cart_id)

    user_id = data.get("user_id")
    is_active = data.get("is_active", True)

    if not user_id:
        raise ValueError("User ID is required")

    user = User.objects.get(id=user_id)

    cart.user = user
    cart.is_active = is_active
    cart.save()

    return cart

def get_all_carts():
    return Cart.objects.all()


def get_user_cart_items(user_id):
    cart_items = CartItem.objects.select_related('product_item', 'cart').filter(
        cart__user_id=user_id,
        is_active=True
    )
    print(cart_items)

    result = []
    for item in cart_items:
        product_item = item.product_item
        result.append({
            'id': item.id,
            'product_name': product_item.product.name,
            'photo': product_item.photo_url,
            'quantity': item.quantity,
            'size': item.size,
            'color':item.color,
            'color_display':Color(item.color).name,
            'size_display': Size(item.size).name,
            'price_per_unit': product_item.price,
            'total_price': product_item.price * item.quantity,
            'available_sizes': [
                {'value': s.value, 'name': s.name}
                for s in Size
            ],
            'available_colors': [
                {'value': c.value, 'name': c.name}
                for c in Color
            ]
        })
    
    return result



def calculate_total_savings(user_id):
    cart_items = CartItem.objects.select_related('product_item').filter(
        cart__user_id=user_id,
        is_active=True
    )

    total_savings = 0
    for item in cart_items:
        product_item = item.product_item
        original_price = product_item.original_price if hasattr(product_item, 'original_price') else product_item.price
        discount_per_unit = max(0, original_price - product_item.price)
        total_savings += discount_per_unit * item.quantity

    return total_savings
