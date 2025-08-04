from E_COMERCE.models import Product, ProductItem
from E_COMERCE.constants.default_values import Size,Color
import os
from uuid import uuid4
from django.conf import settings

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
        'color': product_item.color,
        'availibility': product_item.availibility,
        'created_at': product_item.created_at,
        'product_id': product_item.product.id,
        'product_name':product_item.product.name,
        'product_subcategory_name':product_item.product.subcategory.name,
        'product_category_name':product_item.product.subcategory.category.name,
    }
    return item_data

def create_productitem(data, file):
    try:
        product = Product.objects.get(id=data['product'])

        # Save the uploaded image
        if not file:
            raise Exception("Photo file is missing.")
        
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid4()}{ext}"
        relative_path = f"product_images/{filename}"
        absolute_path = os.path.join(settings.BASE_DIR, 'static', relative_path)

        with open(absolute_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Create product item
        item = ProductItem.objects.create(
            product=product,
            size=data['size'],
            color=data['color'],
            price=data['price'],
            availibility=data['availibility'],
            photo_url=f"/static/{relative_path}",
        )
        return item

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
        # These display values are now safely accessible in the template
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

def get_product_item_by_id(item_id):
    return ProductItem.objects.get(id=item_id)


def get_product_items():
    return ProductItem.objects.select_related('product').all()

