import os
from uuid import uuid4
from django.conf import settings
from django.utils.dateparse import parse_datetime
from E_COMERCE.models import Poster
from E_COMERCE.models import User

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
        dir_path = os.path.join(settings.BASE_DIR, 'static', 'posters')
        os.makedirs(dir_path, exist_ok=True)
        relative_path = f"posters/{filename}"
        absolute_path = os.path.join(dir_path, filename)

        with open(absolute_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        poster = Poster.objects.create(
            created_by=user,
            title=data.get('title', ''),
            description=data.get('description', ''),
            photo_url=f"/static/{relative_path}",
            start_date=parse_datetime(data.get('start_date')) if data.get('start_date') else None,
            end_date=parse_datetime(data.get('end_date')) if data.get('end_date') else None,
        )
        return poster

    except Exception as e:
        raise Exception(f"Failed to create poster: {str(e)}")

def update_poster(poster_id, data, file=None):
    try:
        poster = Poster.objects.get(id=poster_id)
        poster.created_by = User.objects.get(id=data.get('user_id'))
        poster.title = data.get('title', '')
        poster.description = data.get('description', '')
        poster.start_date = parse_datetime(data.get('start_date')) if data.get('start_date') else None
        poster.end_date = parse_datetime(data.get('end_date')) if data.get('end_date') else None

        if file:
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid4()}{ext}"
            dir_path = os.path.join(settings.BASE_DIR, 'static', 'posters')
            os.makedirs(dir_path, exist_ok=True)
            relative_path = f"posters/{filename}"
            absolute_path = os.path.join(dir_path, filename)

            with open(absolute_path, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            poster.photo_url = f"/static/{relative_path}"

        poster.save()
        return poster

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
