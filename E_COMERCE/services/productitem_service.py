from E_COMERCE.models import Product, ProductItem
from E_COMERCE.constants.default_values import Size,Color
import os
from uuid import uuid4
from django.conf import settings
from collections import defaultdict



def get_all_productitems_by_category():
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

    category_to_products = defaultdict(list)
    
    for item in productitems:
        category = item.product.subcategory.category
        category_to_products[category].append(item)
    
    return category_to_products

def get_total_is_not_active_items():
    return ProductItem.objects.filter(is_active = False)

def get_product_items_by_category(category_id):
    items = ProductItem.objects.filter(product__subcategory__category__id= category_id, is_active =True)
    data = []
    if items:
        data = [
            {
                'id':item.id,
                'photo_url':item.photo_url,
                'size':item.size,
                'color':item.color,
                'display_size':Size(item.size).name,
                'display_color':Color(item.color).name,
                'product_name': item.product.name,
                'price': item.price,
            }
            for item in items
        ]
    return data

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

def get_product_items_data(item_id):
    product_item = ProductItem.objects.filter(id=item_id, is_active=True).select_related('product', 'product__subcategory__category').first()

    if not product_item:
        return {}

    # Main product item details
    item_data = {
        'id': product_item.id,
        'photo': product_item.photo_url,
        'price': product_item.price,
        'size': product_item.size,
        'display_size': Size(product_item.size).name,
        'color': product_item.color,
        'display_color': Color(product_item.color).name,
        'availibility': product_item.availibility,
        'created_at': product_item.created_at,
        'product_id': product_item.product.id,
        'product_name':product_item.product.name,
        'product_subcategory_name':product_item.product.subcategory.name,
        'product_category_name':product_item.product.subcategory.category.name,
    }
    return item_data



def create_productitem(request, file):
    try:
        product_id = request.POST.get('product')
        size = int(request.POST.get('size'))
        color = int(request.POST.get('colour'))
        price = int(request.POST.get('price'))
        availibility = int(request.POST.get('availibility'))

        # Debug prints

        product = Product.objects.get(id=product_id, is_active=True)

        # Save the uploaded image
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid4()}{ext}"
        relative_path = f"product_images/{filename}"
        absolute_path = os.path.join(settings.BASE_DIR, 'static', relative_path)

        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)  # ensure dir exists

        with open(absolute_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Create product item instance
        item = ProductItem.objects.create(
            product=product,
            size=size,
            color=color,
            price=price,
            availibility=availibility,
            photo_url=f"/static/{relative_path}",
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
        item.size = item.size = Size[data.get('size')].value
        item.color = Color[data.get('colour')].value
        item.price = int(data.get('price'))
        item.availibility = int(data.get('availibility'))
    
        if file:
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid4()}{ext}"
            dir_path = os.path.join(settings.BASE_DIR, 'static', 'product_images')
            os.makedirs(dir_path, exist_ok=True)
            relative_path = f"product_images/{filename}"
            absolute_path = os.path.join(dir_path, filename)

            with open(absolute_path, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            item.photo_url = f"/static/{relative_path}"

        item.save()
        return item

    except Exception as e:
        raise Exception(f"Update failed: {str(e)}")
    
def get_all_productitems():
    items = ProductItem.objects.select_related('product').all().order_by('id')

    for item in items:
        item.size = Size(item.size).name
        item.color = Color(item.color).name

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

    if not item:
        return None

    return {
        "id": item.id,
        "product_name": item.product.name,
        "price": item.price,
        "photo_url": item.photo_url,
        "size": item.size,
        "size_name": get_size_name(item.size),
        "color": item.color,
        "color_name": get_color_name(item.color),
        "available_sizes": [
            {"value": s.value, "name": s.name}
            for s in Size
        ],
        "available_colors": [
            {"value": c.value, "name": c.name}
            for c in Color
        ] if item.color is not None else []
    }




def get_product_items():
    return ProductItem.objects.select_related('product').all()

