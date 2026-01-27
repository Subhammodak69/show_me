import os
from uuid import uuid4
from django.conf import settings
from django.utils.dateparse import parse_datetime
from E_COMERCE.models import Poster
from E_COMERCE.models import User
from django.utils import timezone

def get_all_posters():
    return Poster.objects.filter(is_active = True)
def create_poster(data, file):
    try:
        user = User.objects.get(id=data['user_id'])

        # Save the uploaded image
        if not file:
            raise Exception("Photo file is missing.")

        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid4()}{ext}"
        
        # ✅ FIXED: Use BASE_DIR instead of STATIC_URL for filesystem path
        dir_path = os.path.join(settings.BASE_DIR, 'static', 'posters')
        os.makedirs(dir_path, exist_ok=True)
        relative_path = f"posters/{filename}"
        absolute_path = os.path.join(dir_path, filename)
        
        print('relativePath=> ', relative_path)
        print('absolutePath=> ', absolute_path)
        
        with open(absolute_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # ✅ FIXED: Full URL path for frontend (same as category)
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
            photo_url=f"/static/{relative_path}",  # ✅ Full URL path
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
        poster.title = data.get('title', poster.title)  # ✅ Keep existing if not provided
        poster.description = data.get('description', poster.description)  # ✅ Keep existing
        
        # ✅ Fixed timezone handling
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
            
            # ✅ FIXED: Use BASE_DIR instead of STATIC_URL
            dir_path = os.path.join(settings.BASE_DIR, 'static', 'posters')
            os.makedirs(dir_path, exist_ok=True)
            relative_path = f"posters/{filename}"
            absolute_path = os.path.join(dir_path, filename)

            with open(absolute_path, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            # ✅ FIXED: Full URL path for frontend
            poster.photo_url = f"/static/{relative_path}"

        # If no file, old photo_url remains unchanged
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
