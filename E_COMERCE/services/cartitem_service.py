from E_COMERCE.models import CartItem

def get_cart_items():
    return CartItem.objects.select_related('cart', 'product_item__product').all()

def cartitem_create(cart_id,product_item_id,size,color,quantity):
    return CartItem.objects.create(
            cart_id=cart_id,
            product_item_id=product_item_id,
            size=size,
            color=color,
            quantity=quantity
        )


def get_cart_item_object(pk):
    return CartItem.objects.get(id = pk ,is_active = True)