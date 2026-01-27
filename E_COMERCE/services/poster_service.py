import os
from uuid import uuid4
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from E_COMERCE.models import User, Poster

def get_all_posters():
    return Poster.objects.filter(is_active = True)

def create_poster(data, file):
    try:
        user = User.objects.get(id=data['user_id'])

        if not file:
            raise Exception("Photo file is missing.")

        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid4()}{ext}"
        relative_path = f"posters/{filename}"
        
        # ✅ CLOUDIOUSINARY: Auto-uploads to cloud
        cloudinary_path = default_storage.save(relative_path, file)
        photo_url = default_storage.url(cloudinary_path)  # Full CDN URL
        
        print(f"Cloudinary path: {cloudinary_path}")
        print(f"CDN URL: {photo_url}")

        start_date = parse_datetime(data.get('start_date')) if data.get('start_date') else None
        if start_date and timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)

        end_date = parse_datetime(data.get('end_date')) if data.get('end_date') else None
        if end_date and timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)

        poster = Poster.objects.create(
            created_by=user,
            title=data.get('title', ''),
            description=data.get('description', ''),
            photo_url=photo_url,  # Full Cloudinary CDN URL
            start_date=start_date,
            end_date=end_date,
        )
        return poster

    except Exception as e:
        raise Exception(f"Failed to create poster: {str(e)}")


def update_poster(poster_id, data, file=None):
    try:
        poster = Poster.objects.get(id=poster_id)
        poster.created_by = User.objects.get(id=data.get('user_id'))
        poster.title = data.get('title', poster.title)
        poster.description = data.get('description', poster.description)
        
        start_date = parse_datetime(data.get('start_date')) if data.get('start_date') else None
        if start_date and timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)
        poster.start_date = start_date
        
        end_date = parse_datetime(data.get('end_date')) if data.get('end_date') else None
        if end_date and timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)
        poster.end_date = end_date

        # Handle new photo if uploaded
        if file:
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid4()}{ext}"
            relative_path = f"posters/{filename}"
            
            # ✅ CLOUDIOUSINARY: Auto-uploads to cloud
            cloudinary_path = default_storage.save(relative_path, file)
            photo_url = default_storage.url(cloudinary_path)
            
            print(f"Cloudinary path: {cloudinary_path}")
            print(f"CDN URL: {photo_url}")

            poster.photo_url = photo_url  # Full Cloudinary CDN URL

        poster.save()
        return poster

    except Poster.DoesNotExist:
        raise Exception("Poster not found.")
    except User.DoesNotExist:
        raise Exception("User not found.")
    except Exception as e:
        raise Exception(f"Update failed: {str(e)}")


def toggle_poster_status(poster_id):
    try:
        poster = Poster.objects.get(id=poster_id)
        poster.is_active = not poster.is_active
        poster.save()
        return poster.is_active
    except Poster.DoesNotExist:
        raise Exception("Poster not found.")
