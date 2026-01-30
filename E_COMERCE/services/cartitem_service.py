from E_COMERCE.models import CartItem

def get_cart_items():
    return CartItem.objects.select_related('cart', 'product_item__product').all()
def get_cart_items_by_cart(cart):
    return CartItem.objects.filter(cart = cart, is_active = True)
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


def toggle_cartitem_status(cartitem_id: int, is_active: bool) -> dict:
    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
        cartitem.is_active = is_active
        cartitem.save()
        return {
            "success": True,
            "new_status": cartitem.is_active
        }
    except CartItem.DoesNotExist:
        return {
            "success": False,
            "error": "CartItem not found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
