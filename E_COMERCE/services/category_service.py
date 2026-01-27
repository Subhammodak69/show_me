from uuid import uuid4
from E_COMERCE.models import Category
import cloudinary
import cloudinary.uploader

def create_category(data, file, user):
    try:
        if not file:
            raise Exception("Photo file is missing.")

        # ✅ SAME CLOUDINARY METHOD AS POSTERS
        result = cloudinary.uploader.upload(
            file,
            folder="category_images",
            resource_type="image",
            public_id=f"category_{uuid4()}",
            overwrite=True,
        )
        
        photo_url = result['secure_url']

        category = Category.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            photo_url=photo_url,  # Full Cloudinary URL!
            created_by=user
        )
        return category

    except Exception as e:
        raise Exception(f"Failed to create category: {str(e)}")

def update_category(category_id, data, file=None):
    try:
        category = Category.objects.get(pk=category_id)
        
        # Update basic fields
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)

        # ✅ NEW PHOTO + OLD PHOTO DELETE (SAME AS POSTERS)
        if file:
            # Delete old Cloudinary image
            if category.photo_url:
                try:
                    # Extract public_id from URL
                    public_id = category.photo_url.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
                    print(f"🗑️ Deleted old category image: {public_id}")
                except Exception as delete_error:
                    print(f"⚠️ Could not delete old image: {delete_error}")

            # Upload new image (SAME METHOD)
            result = cloudinary.uploader.upload(
                file,
                folder="category_images",
                resource_type="image",
                public_id=f"category_{uuid4()}",
                overwrite=True,
            )
            category.photo_url = result['secure_url']
            print(f"✅ New category image: {category.photo_url}")

        category.save()
        return category

    except Category.DoesNotExist:
        raise Exception("Category not found.")
    except Exception as e:
        raise Exception(f"Failed to update category: {str(e)}")

def delete_category(category_id):
    """Delete category and its Cloudinary image"""
    try:
        category = Category.objects.get(pk=category_id)
        
        # Delete Cloudinary image
        if category.photo_url:
            try:
                public_id = category.photo_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id, invalidate=True)
                print(f"🗑️ Deleted category image: {public_id}")
            except Exception as delete_error:
                print(f"⚠️ Could not delete image: {delete_error}")
        
        category.delete()
        return True
        
    except Category.DoesNotExist:
        raise Exception("Category not found.")



def get_category_data(category_id):
    return Category.objects.filter(id=category_id,is_active=True).first()

class CategoryNotFoundError(Exception):
    pass


def get_category_object(category_id):
    try:
        return Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        raise CategoryNotFoundError(f'Category with ID {category_id} not found')


def toggle_category_status(category_id, new_status: bool):
    category = get_category_object(category_id)
    category.is_active = new_status
    category.save()
    return category

def get_all_category():
    categories = Category.objects.all().order_by('id')
    category_data = []
    if categories:
        category_data = [
            {
              'id':category.id,
              'name':category.name,
              'description':category.description,
              'photo_url':category.photo_url,
              'created_by':category.created_by,
              'created_at':category.created_at,
              'is_active' :category.is_active 
            }
            for category in categories
        ]
    return category_data

def get_categories():
    return Category.objects.all()