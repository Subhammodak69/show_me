from E_COMERCE.models import Category
import os
from uuid import uuid4
from django.conf import settings

def create_category(data, file, user):
    try:
        if not file:
            raise Exception("Photo file is missing.")

        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid4()}{ext}"
        relative_path = f"category_images/{filename}"
        absolute_path = os.path.join(settings.BASE_DIR, 'static', relative_path)

        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        with open(absolute_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        category = Category.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            photo_url=f"/static/{relative_path}",
            created_by=user
        )
        return category

    except Exception as e:
        raise Exception(f"Failed to create category: {str(e)}")

   

def update_category(category_id, data, file=None):
    try:
        category = Category.objects.get(pk=category_id)
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)

        # Handle new photo if uploaded
        if file:
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid4()}{ext}"
            relative_path = f"category_images/{filename}"
            absolute_path = os.path.join(settings.BASE_DIR, 'static', relative_path)
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

            with open(absolute_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            category.photo_url = f"/static/{relative_path}"

        # If file not supplied, the old photo_url remains unchanged
        category.save()
        return category

    except Category.DoesNotExist:
        raise Exception("Category not found.")
    except Exception as e:
        raise Exception(f"Failed to update category: {str(e)}")

    

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