from E_COMERCE.models import ProductItem,Wishlist,User
from django.core.exceptions import ObjectDoesNotExist
from E_COMERCE.services import productitem_service

def  wishlist_item_ids(user_id):
    return Wishlist.objects.filter(created_by=user_id, is_active=True).values_list('product_item', flat=True)

def get_wishlist_items(user_id):
    whishlist_items = list(Wishlist.objects.filter(created_by=user_id , is_active = True))
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
                'display_size':Size(item.product_item.size).name,
                'display_color':Color(item.product_item.color).name,
                'color':item.product_item.color,
                'availibility':productitem_service.get_product_items_availibility(item.product_item),
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




from E_COMERCE.models import Wishlist
from E_COMERCE.constants.default_values import Size, Color

def get_all_wishlists():
    wishlists = Wishlist.objects.select_related(
        'created_by',
        'product_item',
        'product_item__product'
    )

    detailed_data = []

    for item in wishlists:
        product_item = item.product_item
        detailed_data.append({
            'id': item.id,
            'created_by': item.created_by.get_full_name() if hasattr(item.created_by, 'get_full_name') else str(item.created_by),
            'product_name': product_item.product.name,
            'size': product_item.size,
            'color': product_item.color,
            'display_size': Size(product_item.size).name,
            'display_color': Color(product_item.color).name,
            'created_at': item.created_at,
            'product_item_id': product_item.id,
        })

    return detailed_data



def get_wishlist_by_id(pk):
    return Wishlist.objects.select_related('created_by', 'product_item__product').get(pk=pk)

def create_wishlist(data):
    user = User.objects.get(id=data['user_id'])
    product_item = ProductItem.objects.get(id=data['product_item_id'])
    return Wishlist.objects.create(
        created_by=user,
        product_item=product_item,
        is_active=data.get('is_active', True)
    )



def update_wishlist(pk, data):
    wishlist = Wishlist.objects.get(pk=pk)
    wishlist.created_by_id = data['user_id']
    wishlist.product_item_id = data['product_item_id']
    wishlist.is_active = data.get('is_active', wishlist.is_active)
    wishlist.save()
    return wishlist


def toggle_wishlist_status(pk, is_active):
    wishlist = Wishlist.objects.get(pk=pk)
    wishlist.is_active = is_active
    wishlist.save()
    return wishlist.is_active
