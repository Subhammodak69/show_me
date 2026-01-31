from E_COMERCE.models import Rating,ProductItem,Product
import cloudinary
import cloudinary.uploader
from uuid import uuid4
from E_COMERCE.models import Product, Rating
from django.shortcuts import get_object_or_404


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

    return data


def get_rating_by_id(pk):
    try:
        return Rating.objects.get(pk=pk, is_active=True)
    except Rating.DoesNotExist:
        return None


def get_all_reviews_for_admin():
    return Rating.objects.all()

def toggle_review_active_status(pk, is_active):
    review = get_object_or_404(Rating, pk=pk)
    review.is_active = is_active
    review.save()
    return review.is_active

def create_rating(data, file, user):
    try:
        product = Product.objects.get(id=data.get('product_id'))
        rating_value = int(data.get('rating'))
        review_text = data.get('review', '')

        photo_url = None  # Will be None if no file

        # ✅ SAME CLOUDINARY METHOD - Optional image upload
        if file:
            result = cloudinary.uploader.upload(
                file,
                folder="rating_photos",
                resource_type="image",
                public_id=f"rating_{uuid4()}",
                overwrite=True,
            )
            photo_url = result['secure_url']
            print(f"✅ Rating photo uploaded: {photo_url}")

        rating = Rating.objects.create(
            product=product,
            photo_url=photo_url,  # Full Cloudinary URL or None
            user=user,
            rating=rating_value,
            review=review_text,
        )
        return rating

    except Product.DoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Failed to create rating: {str(e)}")

def update_rating(rating_id, data, file=None):
    try:
        rating = Rating.objects.get(id=rating_id)
        rating.product = Product.objects.get(id=data.get('product_id'))
        rating.rating = int(data.get('rating'))
        rating.review = data.get('review', rating.review)
        
        # ✅ NEW PHOTO + OLD PHOTO DELETE (SAME PATTERN)
        if file:
            # Delete old Cloudinary image
            if rating.photo_url:
                try:
                    public_id = rating.photo_url.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
                    print(f"🗑️ Deleted old rating image: {public_id}")
                except Exception as delete_error:
                    print(f"⚠️ Could not delete old image: {delete_error}")

            # Upload new image
            result = cloudinary.uploader.upload(
                file,
                folder="rating_photos",
                resource_type="image",
                public_id=f"rating_{uuid4()}",
                overwrite=True,
            )
            rating.photo_url = result['secure_url']
            print(f"✅ New rating image: {rating.photo_url}")

        rating.save()
        return rating

    except Rating.DoesNotExist:
        raise Exception("Rating not found.")
    except Product.DoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Update failed: {str(e)}")

def delete_rating(rating_id):
    """Delete rating and its Cloudinary image"""
    try:
        rating = Rating.objects.get(id=rating_id)
        
        # Delete Cloudinary image
        if rating.photo_url:
            try:
                public_id = rating.photo_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id, invalidate=True)
                print(f"🗑️ Deleted rating image: {public_id}")
            except Exception as delete_error:
                print(f"⚠️ Could not delete image: {delete_error}")
        
        rating.delete()
        return True
        
    except Rating.DoesNotExist:
        raise Exception("Rating not found.")


def deactivate_rating(rating):
    rating.is_active = False
    rating.save()
    return rating

def get_ratings_data(product_id):
    return list(
        Rating.objects.filter(product=product_id, is_active=True)
        .values('id', 'user', 'rating', 'review','photo_url') 
    )
