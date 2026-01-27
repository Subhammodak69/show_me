from uuid import uuid4
from dateutil import parser
from django.utils import timezone
from E_COMERCE.models import User, Poster
import cloudinary
import cloudinary.uploader

def get_all_posters():
    return Poster.objects.filter(is_active = True)


def create_poster(data, file):
    try:
        user = User.objects.get(id=data['user_id'])

        if not file:
            raise Exception("Photo file is missing.")

        # ✅ FIXED - Remove format="auto"
        result = cloudinary.uploader.upload(
            file,
            folder="posters",
            resource_type="image",
            public_id=f"poster_{uuid4()}",
            overwrite=True,
            # format="auto"  ❌ REMOVED - This causes the error!
        )
        
        # ✅ Save the secure Cloudinary URL
        photo_url = result['secure_url']
        print(f"✅ Uploaded: {photo_url}")

        # Parse dates
        start_date = None
        if data.get('start_date'):
            start_date = parser.parse(data['start_date'])
            if timezone.is_naive(start_date):
                start_date = timezone.make_aware(start_date)

        end_date = None
        if data.get('end_date'):
            end_date = parser.parse(data['end_date'])
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)

        poster = Poster.objects.create(
            created_by=user,
            title=data.get('title', ''),
            description=data.get('description', ''),
            photo_url=photo_url,
            start_date=start_date,
            end_date=end_date,
        )
        
        return poster

    except Exception as e:
        raise Exception(f"Failed to create poster: {str(e)}")



def update_poster(poster_id, data, file=None):
    try:
        poster = Poster.objects.get(id=poster_id)
        user = User.objects.get(id=data.get('user_id'))
        
        # Update basic fields
        poster.created_by = user
        poster.title = data.get('title', poster.title)
        poster.description = data.get('description', poster.description)

        # ✅ Django-native date parsing (no dateutil needed)
        start_date = None
        if data.get('start_date'):
            try:
                start_date = timezone.datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except:
                start_date = timezone.make_aware(
                    timezone.datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
                )
        poster.start_date = start_date

        end_date = None
        if data.get('end_date'):
            try:
                end_date = timezone.datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except:
                end_date = timezone.make_aware(
                    timezone.datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')
                )
        poster.end_date = end_date

        # ✅ NEW PHOTO UPLOAD + OLD PHOTO DELETE
        if file:
            # Delete old Cloudinary image (if exists)
            if poster.photo_url:
                try:
                    # Extract public_id from Cloudinary URL
                    public_id = poster.photo_url.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
                    print(f"🗑️ Deleted old image: {public_id}")
                except:
                    print("⚠️ Could not delete old image")

            # Upload new image to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder="posters",
                resource_type="image",
                public_id=f"poster_{uuid4()}",
                overwrite=True
            )
            
            # Save new Cloudinary URL
            poster.photo_url = result['secure_url']
            print(f"✅ New image uploaded: {poster.photo_url}")

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
