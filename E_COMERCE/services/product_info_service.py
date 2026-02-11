from E_COMERCE.models import ItemInfo,ProductItem
from E_COMERCE.constants.default_values import Size,Color
import cloudinary
import cloudinary.uploader
from uuid import uuid4
from E_COMERCE.services import cart_service,product_info_service
from django.db.models import Sum
import json

def get_iteminfo_objects_by_product_item(product_item_id):
    """
    Get all variants for a ProductItem (size/color combinations)
    """
    return ItemInfo.objects.filter(product_item_id=product_item_id)

def get_varient_object(varient_id):
    return ItemInfo.objects.filter(id = varient_id, is_active = True).first()


def get_iteminfo_by_product_item(product_item,size,color):
    return ItemInfo.objects.filter(product_item=product_item,size = size,color = color,is_active = True).first()

def get_stock_by_product_details(product_item, color, size):
    total_stock = ItemInfo.objects.filter(
        product_item=product_item, 
        color=color, 
        size=size, 
        is_active=True
    ).aggregate(stock=Sum('stock'))['stock'] or 0
    return total_stock

def get_product_info_details(product_item):
    items = ItemInfo.objects.filter(product_item=product_item, is_active=True)
    item_data = []
    if items:
        item_data = [
            {
                'id': item.id,
                'size': item.size,
                'display_size': Size(item.size).name,
                'color': item.color,
                'display_color': Color(item.color).name,
                'image': item.photo_url,
                'stock': item.stock 
            }
            for item in items
        ]
    return item_data



def get_all_iteminfos():
    infos = ItemInfo.objects.all().order_by('-created_at')
    data = []
    if infos:
        data = [
            {
                'id':i.id,
                'size':i.size,
                'color':i.color,
                'display_color':Color(i.color).name,
                'display_size':Size(i.size).name,
                'stock':i.stock,
                'created_at':i.created_at,
                'is_active':i.is_active,
                'product_item':i.product_item,
                'photo_url':i.photo_url
            }
            for i in infos
        ]
    return data

def get_iteminfo_object(iteminfo_id):
    return ItemInfo.objects.select_related('product_item').get(id=iteminfo_id)
def get_iteminfo_by_id(info_id):
    return ItemInfo.objects.filter(id = info_id, is_active = True).first()

def get_item_data_by_varient(variant_id):
    variant = get_iteminfo_object(variant_id)
    
    if not variant:
        return None
        
    discount = cart_service.get_discount_by_id(variant.product_item)
    sale_price = (variant.product_item.price) - discount
    
    # 🔥 Get ALL variants for this product
    all_variants = product_info_service.get_iteminfo_objects_by_product_item(variant.product_item.id)
    
    # 🔥 Build variants JSON (UNCHANGED - already good)
    variants_json = []
    for v in all_variants:
        variants_json.append({
            'id': v.id,
            'size_value': v.size,
            'display_size': Size(v.size).name,
            'color_value': v.color,
            'display_color': Color(v.color).name if v.color else None,
            'stock': v.stock,
            'price': v.product_item.price,
            'image': v.photo_url,
            'product_item': v.product_item.id
        })
    
    variants_json_string = json.dumps(variants_json, ensure_ascii=False)
    
    # 🔥 FIXED: UNIQUE SIZE OPTIONS (NO DUPLICATES)
    size_options = get_unique_size_options(all_variants)
    
    # 🔥 FIXED: UNIQUE COLOR OPTIONS (NO DUPLICATES)  
    color_options = get_unique_color_options(all_variants)
    
    data = {
        'id': variant.id,
        'quantity': 1,
        'size': variant.size,
        'size_display': Size(variant.size).name,
        'color': variant.color,
        'color_display': Color(variant.color).name if variant.color else None,
        'size_options': size_options,  # ✅ UNIQUE
        'color_options': color_options,  # ✅ UNIQUE
        'variants_json': variants_json_string,
        'product_name': variant.product_item.product.name,
        'product_price': variant.product_item.price,
        'product_photo': variant.photo_url,
        'price': variant.product_item.price,
        'discount': discount,
        'total_price': sale_price,
        'product_item': variant.product_item.id,
    }
    return data


# 🔥 NEW HELPER FUNCTIONS - Add these to your service
def get_unique_size_options(all_variants):
    """Get unique sizes with display names - NO DUPLICATES"""
    unique_sizes = {}
    for variant in all_variants:
        if variant.size and variant.stock > 0:  # Only in-stock sizes
            size_name = Size(variant.size).name
            unique_sizes[variant.size] = {
                'value': variant.size,
                'name': size_name
            }
    
    # Convert to list sorted by size value
    return sorted([v for v in unique_sizes.values()], key=lambda x: x['value'])


def get_unique_color_options(all_variants):
    """Get unique colors with display names - NO DUPLICATES"""
    unique_colors = {}
    for variant in all_variants:
        if variant.color and variant.stock > 0:  # Only in-stock colors
            color_name = Color(variant.color).name
            unique_colors[variant.color] = {
                'value': variant.color,
                'name': color_name
            }
    
    # Convert to list sorted by color value
    return sorted([v for v in unique_colors.values()], key=lambda x: x['value'])



def get_all_size_options_by_info_id(variant_id):
    variant = get_iteminfo_object(variant_id)
    options = ItemInfo.objects.filter(product_item = variant.product_item,is_active = True)
    data = []
    if options:
        data = [
            {   
                'name': Size(option.size).name,
                'value': Size(option.size).value
            }
            for option in options if option.stock > 0
        ]
    return data

def get_all_color_options_by_info_id(variant_id):
    variant = get_iteminfo_object(variant_id)
    options = ItemInfo.objects.filter(product_item = variant.product_item,is_active = True)
    data = []
    if options:
        data = [
            {   
                'name': Color(option.color).name,
                'value': Color(option.color).value
            }
            for option in options if option.stock > 0
        ]
    return data

def get_active_products():
    return ProductItem.objects.filter(is_active=True)

def get_size_choices_dict():
    data = [
        {
            'value':size.value,
            'name':size.name
        }
        for size in Size
    ]
    return data

def get_colour_choices_dict():
    data = [
        {
            'value':color.value,
            'name':color.name
        }
        for color in Color
    ]
    return data

def create_iteminfo(request, photo_file):
    try:
        product_item_id = request.POST.get('product_item')
        size = int(request.POST.get('size'))
        color = int(request.POST.get('color'))
        stock = int(request.POST.get('stock', 0))

        # Validate ProductItem exists and is active
        product_item = ProductItem.objects.get(id=product_item_id, is_active=True)

        if not photo_file:
            raise Exception("Photo file is missing.")

        # ✅ SAME CLOUDINARY METHOD - Direct uploader (EXACTLY like productitem)
        result = cloudinary.uploader.upload(
            photo_file,
            folder="iteminfo_images",  # Different folder for ItemInfo
            resource_type="image",
            public_id=f"iteminfo_{uuid4()}",
            overwrite=True,
        )
        
        photo_url = result['secure_url']
        print(f"✅ ItemInfo uploaded: {photo_url}")

        item = ItemInfo.objects.create(
            product_item=product_item,
            photo_url=photo_url,  # Full Cloudinary CDN URL
            size=size,
            color=color,
            stock=stock,
            is_active=True
        )

        return item

    except ProductItem.DoesNotExist:
        raise Exception("Invalid or inactive product item selected.")
    except Exception as e:
        raise Exception(f"Failed to create item info: {str(e)}")

def update_iteminfo(iteminfo_id, data, photo_file=None):
    try:
        item = ItemInfo.objects.get(id=iteminfo_id)
        item.product_item = ProductItem.objects.get(id=data.get('product_item'), is_active=True)
        item.size = int(data.get('size'))
        item.color = int(data.get('color'))
        item.stock = int(data.get('stock', 0))
        
        # ✅ NEW PHOTO + OLD PHOTO DELETE (EXACTLY like productitem)
        if photo_file:
            # Delete old Cloudinary image
            if item.photo_url:
                try:
                    # Extract public_id from Cloudinary URL
                    public_id = item.photo_url.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
                    print(f"🗑️ Deleted old iteminfo image: {public_id}")
                except Exception as delete_error:
                    print(f"⚠️ Could not delete old image: {delete_error}")

            # Upload new image (SAME METHOD)
            result = cloudinary.uploader.upload(
                photo_file,
                folder="iteminfo_images",
                resource_type="image",
                public_id=f"iteminfo_{uuid4()}",
                overwrite=True,
            )
            item.photo_url = result['secure_url']
            print(f"✅ New iteminfo image: {item.photo_url}")

        item.save()
        return item

    except ItemInfo.DoesNotExist:
        raise Exception("Item info not found.")
    except ProductItem.DoesNotExist:
        raise Exception("Product item not found.")
    except Exception as e:
        raise Exception(f"Update failed: {str(e)}")

def toggle_iteminfo_status(iteminfo_id):
    try:
        item = ItemInfo.objects.get(id=iteminfo_id)
        item.is_active = not item.is_active
        item.save()
        return item.is_active
    except ItemInfo.DoesNotExist:
        raise Exception("Item info not found.")

def get_photo_by_color_size(product_item,color,size):
    variant = ItemInfo.objects.filter(product_item = product_item,size = size,color = color,is_active = True).first()
    return variant.photo_url