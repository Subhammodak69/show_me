from E_COMERCE.models import ItemInfo,ProductItem
from E_COMERCE.constants.default_values import Size,Color
import cloudinary
import cloudinary.uploader
from uuid import uuid4

def get_product_info_details(product_item):
    items = ItemInfo.objects.filter(product_item = product_item, is_active = True)
    item_data = []
    if items:
        item_data = [
            {
                'id':item.id,
                'size':item.size,
                'display_size':Size(item.size).name,
                'color':item.color,
                'display_color':Color(item.color).name,
                'image':item.photo_url,
            }
            for item in items
        ]
    return item_data


def get_all_iteminfos():
    return ItemInfo.objects.select_related('product_item').all().order_by('-created_at')

def get_iteminfo_object(iteminfo_id):
    return ItemInfo.objects.select_related('product_item').get(id=iteminfo_id)

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
