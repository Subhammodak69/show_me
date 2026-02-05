from E_COMERCE.models import Product, ProductItem,Offer,Rating,ItemInfo
from E_COMERCE.constants.default_values import Size,Color
import cloudinary
import cloudinary.uploader
from uuid import uuid4
from collections import defaultdict
from E_COMERCE.services import product_info_service,offer_service,productitem_service
import json
from django.core.paginator import Paginator


def get_average_rating(ratings):
    if ratings:
        return sum(rating.rating for rating in ratings) / len(ratings)
    return 0

def get_all_productitems_by_category():
    print("come")
    """
    Returns a dict mapping Category instances to a list of their active ProductItems.
    Only active categories, subcategories, products, and product items are included.
    """
    # Prefetch productitems through product -> subcategory -> category
    productitems = ProductItem.objects.filter(
        is_active=True,
        product__is_active=True,
        product__subcategory__is_active=True,
        product__subcategory__category__is_active=True
    ).select_related(
        'product__subcategory__category'
    ).order_by('product__subcategory__category__name')
    print("get")
    category_to_products = defaultdict(list)
    
    for item in productitems:
        category = item.product.subcategory.category
        item.price = productitem_service.get_prduct_sale_and_orignal_price_by_product_item(item)
        # print(item.price)
        category_to_products[category].append(item)
    print("go")
    return category_to_products

def get_total_is_not_active_items():
    return ProductItem.objects.filter(is_active = False)

def get_prduct_sale_and_orignal_price_by_product_item(product_item):
    item = ProductItem.objects.filter(id = product_item.id,is_active = True).first()
    offer = offer_service.get_offer_by_product(item.product)
    sale_price = item.price - offer.discount_value if offer and offer.discount_value else item.price
    data = {
        'original_price':item.price,
        'sale_price':sale_price
    }
    return data

# In get_product_items_by_category_paginated - RETURN page_obj.object_list instead
def get_product_items_by_category_paginated(category_id, page=1):
    items_qs = ProductItem.objects.filter(
        product__subcategory__category__id=category_id, 
        is_active=True
    ).order_by('-id')
    
    paginator = Paginator(items_qs, 12)
    page_obj = paginator.get_page(page)
    
    data = []
    for item in page_obj.object_list:  # Use .object_list
        data.append({
            'id': item.id,
            'photo_url': item.photo_url,  
            'product_name': item.product.name,
            'price_data': get_prduct_sale_and_orignal_price_by_product_item(item),
            'rating_count': len(get_all_rating_by_product(item.product)),
            'rating': get_average_rating(get_all_rating_by_product(item.product))
        })
    
    return {
        'items': data,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None
    }

def get_product_item_related_product_items(product_id):
    items = list( ProductItem.objects.filter(product__id = product_id,is_active = True))
    data = []
    if items:
        data = [
            {
                'id': item.id,
                'photo':item.photo_url,
            }
            for item in items
        ]
    return data

def get_size(size):
    return Size(size).name

def get_size_choices_dict():
    return {size.name: size.value for size in Size}

def get_colour_choices_dict():
    return {colour.name: colour.value for colour in Color}

def get_product_items_availibility(product_item):
    return ItemInfo.objects.filter(product_item = product_item).count()



def get_product_items_data(item_id):
    product_item = ProductItem.objects.filter(id=item_id, is_active=True).select_related('product', 'product__subcategory__category').first()
    availibility = get_product_items_availibility(product_item)
    
    offer = Offer.objects.filter(product=product_item.product, is_active=True).first()
    discount_amount = 0
    ratings = get_all_rating_by_product(product_item.product)
    if ratings:
        rating = sum(rating.rating for rating in ratings) / len(ratings)
    else:
        rating = 0
    
    if offer:
        discount_amount = offer.discount_value

    if not product_item:
        return {}

    product_info_data = product_info_service.get_product_info_details(product_item.id)
    
    # ✅ FIXED JSON LOGIC - Only one if statement
    product_infos_json = '[]'  # Default empty array
    if product_info_data and len(product_info_data) > 0:
        variants_list = [
            {
                'id': item['id'],
                'display_size': item['display_size'],
                'stock': item.get('stock', 0),  # Will be 0 until you add stock field
                'display_color': item['display_color'],
                'image': item.get('image', '')
            }
            for item in product_info_data
        ]
        product_infos_json = json.dumps(variants_list)

    item_data = {
        'id': product_item.id,
        'photo': product_item.photo_url,
        'price': product_item.price,
        'product_infos': product_info_data,
        'product_infos_json': product_infos_json,  # ✅ This is what template uses
        # ... rest of your fields unchanged
        'created_at': product_item.created_at,
        'product_id': product_item.product.id,
        'product_description': product_item.product.description,
        'product_name': product_item.product.name,
        'product_subcategory_name': product_item.product.subcategory.name,
        'product_subcategory_description': product_item.product.subcategory.description,
        'product_category_name': product_item.product.subcategory.category.name,
        'product_category_description': product_item.product.subcategory.category.description,
        'offer': offer.title if offer else '',
        'discount': discount_amount,
        'sale_price': (product_item.price) - (discount_amount),
        'offer_description': offer.description if offer else '',
        'availibility': availibility,
        'rating': rating,
        'rating_count': len(ratings)
    }
    return item_data


def get_all_rating_by_product(product):
    return Rating.objects.filter(product = product,is_active=True)



def create_productitem(request, file):
    try:
        product_id = request.POST.get('product')
        price = int(request.POST.get('price'))

        product = Product.objects.get(id=product_id, is_active=True)

        if not file:
            raise Exception("Photo file is missing.")

        # ✅ SAME CLOUDINARY METHOD - Direct uploader
        result = cloudinary.uploader.upload(
            file,
            folder="product_images",
            resource_type="image",
            public_id=f"product_{uuid4()}",
            overwrite=True,
        )
        
        photo_url = result['secure_url']
        # print(f"✅ Product item uploaded: {photo_url}")

        item = ProductItem.objects.create(
            product=product,
            price=price,
            photo_url=photo_url,  # Full Cloudinary CDN URL
        )

        return item

    except Product.DoesNotExist:
        raise Exception("Invalid or inactive product selected.")
    except Exception as e:
        raise Exception(f"Failed to create product item: {str(e)}")

def update_productitem(item_id, data, file=None):
    try:
        item = ProductItem.objects.get(id=item_id)
        item.product = Product.objects.get(id=data.get('product'))
        item.price = int(data.get('price'))
        
        # ✅ NEW PHOTO + OLD PHOTO DELETE (SAME AS OTHERS)
        if file:
            # Delete old Cloudinary image
            if item.photo_url:
                try:
                    public_id = item.photo_url.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
                    print(f"🗑️ Deleted old product image: {public_id}")
                except Exception as delete_error:
                    print(f"⚠️ Could not delete old image: {delete_error}")

            # Upload new image (SAME METHOD)
            result = cloudinary.uploader.upload(
                file,
                folder="product_images",
                resource_type="image",
                public_id=f"product_{uuid4()}",
                overwrite=True,
            )
            item.photo_url = result['secure_url']
            print(f"✅ New product image: {item.photo_url}")

        item.save()
        return item

    except ProductItem.DoesNotExist:
        raise Exception("Product item not found.")
    except Product.DoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Update failed: {str(e)}")

def delete_productitem(item_id):
    """Delete product item and its Cloudinary image"""
    try:
        item = ProductItem.objects.get(id=item_id)
        
        # Delete Cloudinary image
        if item.photo_url:
            try:
                public_id = item.photo_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id, invalidate=True)
                print(f"🗑️ Deleted product image: {public_id}")
            except Exception as delete_error:
                print(f"⚠️ Could not delete image: {delete_error}")
        
        item.delete()
        return True
        
    except ProductItem.DoesNotExist:
        raise Exception("Product item not found.")




    
def get_all_productitems():
    items = ProductItem.objects.select_related('product').all().order_by('id')
    return items

def get_active_products():
    return Product.objects.filter(is_active=True)

def get_productitem_object(productitem_id):
    return ProductItem.objects.get(id = productitem_id,is_active = True)

def toggle_productitem_status(productitem_id):
    try:
        item = ProductItem.objects.get(id=productitem_id)
        item.is_active = not item.is_active
        item.save()
        return item.is_active
    except ProductItem.DoesNotExist:
        raise Exception("ProductItem not found.")


def get_size_name(value):
    return Size(value).name if value is not None else None

def get_color_name(value):
    return Color(value).name if value is not None else None

def get_product_item_by_id(item_id):
    item = (
        ProductItem.objects
        .select_related('product')
        .filter(id=item_id, is_active=True)
        .first()
    )
    offer = Offer.objects.filter(product = item.product,is_active=True).first()
    discount_amount = 0
    if offer:
        discount_amount = offer.discount_value
        
    if not item:
        return None

    return {
        "id": item.id,
        "product_name": item.product.name,
        "price": (item.price),
        "photo_url": item.photo_url,
        'discount_amount':discount_amount,
        'total':(item.price)-(discount_amount),
    }




def get_product_items():
    return ProductItem.objects.select_related('product').all()

