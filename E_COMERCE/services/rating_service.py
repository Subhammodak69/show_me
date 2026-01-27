from E_COMERCE.models import Rating,ProductItem,Product
import os
from uuid import uuid4
from django.core.files.storage import default_storage


def get_all_ratings_by_product_item_id(item_id):
    productitem = ProductItem.objects.filter(id=item_id, is_active=True).first()
    ratings = Rating.objects.filter(product=productitem.product, is_active=True).order_by("-created_at")

    # Add rating_range and empty_range attributes to each rating object
    for rating in ratings:
        rating.rating_range = range(rating.rating)
        rating.empty_range = range(5 - rating.rating)

    data = []
    if ratings:
        data = [
            {
                'id': i.id,
                'review': i.review,
                'photo': i.photo_url if i.photo_url else None,
                'created_by': i.user,
                'created_by_fullname': f"{i.user.first_name} {i.user.last_name}",
                'created_at': i.created_at,
                'rating_range': i.rating_range,
                'empty_range': i.empty_range,
            }
            for i in ratings
        ]

    print(data)
    return data


def get_rating_by_id(pk):
    try:
        return Rating.objects.get(pk=pk, is_active=True)
    except Rating.DoesNotExist:
        return None


def create_rating(data, file, user):
    try:
        photo_url = ''  # Default photo URL if no file is uploaded

        if file:
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid4()}{ext}"
            relative_path = f"rating_photos/{filename}"
            
            # ✅ CLOUDIOUSINARY: Auto-uploads to cloud
            cloudinary_path = default_storage.save(relative_path, file)
            photo_url = default_storage.url(cloudinary_path)  # Full CDN URL
            
            print(f"Cloudinary path: {cloudinary_path}")
            print(f"CDN URL: {photo_url}")

        product = Product.objects.get(id=data.get('product_id'))
        rating_value = int(data.get('rating'))
        review_text = data.get('review', '')

        rating = Rating.objects.create(
            product=product,
            photo_url=photo_url,  # Full Cloudinary CDN URL or empty string
            user=user,
            rating=rating_value,
            review=review_text,
        )
        return rating

    except Product.DoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Failed to create rating: {str(e)}")



def update_rating(rating, data):
    for attr, value in data.items():
        setattr(rating, attr, value)
    rating.save()
    return rating

def deactivate_rating(rating):
    rating.is_active = False
    rating.save()
    return rating

def get_ratings_data(product_id):
    return list(
        Rating.objects.filter(product=product_id, is_active=True)
        .values('id', 'user', 'rating', 'review','photo_url') 
    )
