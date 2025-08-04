from E_COMERCE.models import Cart, CartItem, ProductItem,User
from django.shortcuts import get_object_or_404

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, defaults={"is_active": True})
    return cart
def get_cart_details(user):
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if not cart:
        return CartItem.objects.none()
    return cart.items.select_related('product_item')

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