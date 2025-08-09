from E_COMERCE.models import Order, OrderItem,ProductItem,CartItem,User
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

def create_order_from_cart(user, address):
    cart_items = CartItem.objects.filter(cart__user=user, is_active=True)
    if not cart_items.exists():
        raise ValueError("Cart is empty.")

    # Set initial total_price=0 to avoid IntegrityError
    order = Order.objects.create(
        created_by=user,
        delivery_address=address,
        total_price=0  # ✅ required
    )

    total = 0
    for item in cart_items:
        OrderItem.objects.create(
            order_id=order,
            product_item=item.product_item,
            quantity=item.quantity,
            size=item.size
        )
        total += item.product_item.price * item.quantity

    order.total_price = total
    order.save()

    # Mark all cart items inactive
    cart_items.update(is_active=False)

    return order



def create_direct_order(user, product_item_id, quantity, size, address):
    item = ProductItem.objects.get(id=product_item_id)

    order = Order.objects.create(
        created_by=user,
        delivery_address=address,
        total_price=item.price * quantity
    )
    OrderItem.objects.create(
        order_id=order,
        product_item=item,
        quantity=quantity,
        size=size
    )
    return order




def get_user_orders(user):
    """Return active orders for a user, with all needed related data prefetched."""
    return (
        Order.objects.filter(created_by=user, is_active=True)
        .prefetch_related(
            'orderitems',
            'orderitems__product_item',
            'orderitems__product_item__product'
        )
        .order_by('-created_at')
    )






def get_all_orders():
    return Order.objects.all().order_by('id')

def get_all_users():
    return User.objects.all()

def get_order_by_id(order_id):
    return get_object_or_404(Order, pk=order_id)

def get_user_by_id(user_id):
    return get_object_or_404(User, pk=user_id)

def create_order(data):
    user = get_user_by_id(data['created_by'])
    return Order.objects.create(
        created_by=user,
        delivery_address=data['delivery_address'],
        status=data['status'],
        total_price=data['total_price'],
        is_active=data['is_active']
    )

def update_order(order_id, data):
    order = get_order_by_id(order_id)
    user = get_user_by_id(data['created_by'])

    order.created_by = user
    order.delivery_address = data['delivery_address']
    order.status = data['status']
    order.total_price = data['total_price']
    order.is_active = data['is_active']
    order.save()
    return order


def toggle_order_active_status(pk, is_active):
    order = get_object_or_404(Order, pk=pk)
    order.is_active = is_active
    order.save()
    return order.is_active


def get_total_order_count():
    return Order.objects.count()

def get_recent_orders():
    return Order.objects.select_related('created_by').order_by('-id')[:5]

def get_order_tracking_info(order_id):
    """
    Returns a dict with order, its items, expected delivery date, and display status.
    Raises Http404 if not found.
    """
    order = get_object_or_404(Order.objects.select_related('created_by'), id=order_id)
    order_items = order.orderitems.select_related('product_item__product').all()
    expected_delivery = order.created_at + timedelta(days=5)
    status_display = order.get_status_display() if hasattr(order, 'get_status_display') else order.status

    return {
        'order': order,
        'order_items': order_items,
        'expected_delivery': expected_delivery,
        'status_display': status_display,
    }


def delete_order_and_items(order_id):
    """
    Deletes the order and its associated order items.
    Returns True if deletion successful, raises exceptions otherwise.
    """
    try:
        order = Order.objects.get(id=order_id)
        # Explicit delete of related orderitems (optional since cascade handles it)
        OrderItem.objects.filter(order_id=order).delete()
        order.delete()
        return True
    except Order.DoesNotExist:
        raise ObjectDoesNotExist("Order not found.")