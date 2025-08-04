from E_COMERCE.models import ProductItem,Wishlist,User
from django.core.exceptions import ObjectDoesNotExist

def  wishlist_item_ids(user_id):
    return Wishlist.objects.filter(created_by=user_id, is_active=True).values_list('product_item', flat=True)

def get_wishlist_items(user_id):
    whishlist_items = list(Wishlist.objects.filter(created_by=user_id , is_active = True))
    print(whishlist_items)
    items_data = []
    if whishlist_items:
        items_data = [
            {   
                'wishlist_id': item.id,
                'id':item.product_item.id,
                'photo': item.product_item.photo_url,
                'price':item.product_item.price,
                'name': item.product_item.product.name,
                'size':item.product_item.size,
                'color':item.product_item.color,
                'availibility':item.product_item.availibility,
                'description':item.product_item.product.description,
            }
            for item in whishlist_items
        ]
    return items_data

def toggle_user_wishlist(user,item_id):
    try:
        product_item = ProductItem.objects.get(id=item_id, is_active=True)

        wishlist_item, created = Wishlist.objects.get_or_create(
            created_by=user,
            product_item=product_item,
            defaults={'is_active': True}
        )

        if not created:
            # If item already exists, toggle its active status
            wishlist_item.is_active = not wishlist_item.is_active
            wishlist_item.save()

        return 'added' if wishlist_item.is_active else 'removed'

    except ProductItem.DoesNotExist:
        raise ObjectDoesNotExist("Product item not found")
    
def delete_wishlist_item_by_id(wishlist_item_id):
    item = Wishlist.objects.get(id = wishlist_item_id , is_active = True)
    item.is_active = False
    item.save()
    return item




def get_all_wishlists():
    return Wishlist.objects.select_related('created_by', 'product_item__product')

def get_wishlist_by_id(pk):
    return Wishlist.objects.select_related('created_by', 'product_item__product').get(pk=pk)

def create_wishlist(data):
    user = User.objects.get(id=data['created_by'])
    product_item = ProductItem.objects.get(id=data['product_item'])
    return Wishlist.objects.create(
        created_by=user,
        product_item=product_item,
        is_active=data.get('is_active', True)
    )

def update_wishlist(pk, data):
    wishlist = Wishlist.objects.get(pk=pk)
    wishlist.created_by_id = data['created_by']
    wishlist.product_item_id = data['product_item']
    wishlist.is_active = data.get('is_active', wishlist.is_active)
    wishlist.save()
    return wishlist

def toggle_wishlist_status(pk, is_active):
    wishlist = Wishlist.objects.get(pk=pk)
    wishlist.is_active = is_active
    wishlist.save()
    return wishlist.is_active
