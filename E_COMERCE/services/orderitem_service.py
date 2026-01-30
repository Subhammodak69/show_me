from django.shortcuts import get_object_or_404
from E_COMERCE.models import OrderItem, Order, ProductItem

def get_all_orderitems():
    return OrderItem.objects.select_related('product_item', 'order_id').order_by('-created_at')

def get_all_orders():
    return Order.objects.all()

def get_all_product_items():
    return ProductItem.objects.all()

def create_orderitem(data):
    order = get_object_or_404(Order, pk=data['order_id'])
    product_item = get_object_or_404(ProductItem, pk=data['product_item'])
    return OrderItem.objects.create(
        order_id=order,
        product_item=product_item,
        quantity=data['quantity'],
        price=data['price'],
        color = data['color'],
        size=data['size'],
        is_active=data['is_active']
    )

def toggle_orderitem_status(pk, is_active):
    item = get_object_or_404(OrderItem, pk=pk)
    item.is_active = is_active
    item.save()
    return item.is_active


def get_orderitem_by_id(pk):
    return get_object_or_404(OrderItem, pk=pk)

def update_orderitem(pk, data):
    item = get_orderitem_by_id(pk)
    item.order_id_id = data['order_id']
    item.product_item_id = data['product_item']
    item.quantity = data['quantity']
    item.price = data['price']
    item.color = data['color']
    item.size = data['size']
    item.is_active = data['is_active']
    item.save()
    return item

def get_all_order_items_by_order_id(order):
    return OrderItem.objects.filter(order_id = order, is_active = True)