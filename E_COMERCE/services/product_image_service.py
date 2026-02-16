from E_COMERCE.models import ProductImage, ProductItem
import cloudinary
import uuid
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

def get_all_images():
    """Get all product images (both active/inactive for admin)"""
    return ProductImage.objects.all().order_by('-created_at')

def create_image(data, file):
    try:
        # Validate product
        product_item = ProductItem.objects.get(id=data['product_item_id'])

        if not file:
            raise Exception("Photo file is missing.")

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder="product_images",
            resource_type="image",
            public_id=f"product_image_{uuid.uuid4()}",
            overwrite=True,
        )
        
        # Save secure Cloudinary URL
        photo_url = result['secure_url']
        print(f"✅ Product image uploaded: {photo_url}")

        # Create image
        image = ProductImage.objects.create(
            product_item=product_item,
            photo_url=photo_url,
            is_active=data.get('is_active', True),
        )
        
        return image

    except ProductItem.DoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Failed to create image: {str(e)}")

def update_image(image_id, data, file=None):
    try:
        image = ProductImage.objects.get(id=image_id)
        product_item = ProductItem.objects.get(id=data['product_item_id'])
        
        # Update basic fields
        image.product_item = product_item
        image.is_active = data.get('is_active', image.is_active)

        # Handle new photo upload
        if file:
            # Delete old Cloudinary image
            if image.photo_url:
                try:
                    # Extract public_id from Cloudinary URL
                    public_id = image.photo_url.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
                    print(f"🗑️ Deleted old image: {public_id}")
                except:
                    print("⚠️ Could not delete old image")

            # Upload new image
            result = cloudinary.uploader.upload(
                file,
                folder="product_images",
                resource_type="image",
                public_id=f"product_image_{uuid.uuid4()}",
                overwrite=True
            )
            
            image.photo_url = result['secure_url']
            print(f"✅ New product image uploaded: {image.photo_url}")

        image.save()
        return image

    except ProductImage.DoesNotExist:
        raise Exception("Image not found.")
    except ProductItem.DoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Update failed: {str(e)}")

def toggle_image_status(image_id):
    try:
        image = ProductImage.objects.get(id=image_id)
        image.is_active = not image.is_active
        image.save()
        return image.is_active
    except ProductImage.DoesNotExist:
        raise Exception("Image not found.")


def get_extra_product_images(product_item_id):
    """Get active product images for dynamic showcase"""
    product_item = ProductItem.objects.get(id = product_item_id,is_active = True)
    images = ProductImage.objects.filter(
        is_active=True,
        product_item = product_item
    )
    
    extra_product_images = []
    for img in images:
        extra_product_images.append({
            'id': img.id,
            'photo_url': img.photo_url,
        })
    
    return extra_product_images
