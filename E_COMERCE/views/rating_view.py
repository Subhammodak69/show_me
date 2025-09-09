from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from E_COMERCE.services.rating_service import *
from E_COMERCE.constants.decorators import *
import json


class RatingCreateView(View, EnduserRequiredMixin):
    def post(self, request):
        try:
            print("helllooo")
            data = json.loads(request.body.decode('utf-8'))  # parse JSON body
            
            rating_data = {
                'product_id': data.get('product_id'),
                'user_id': data.get('user_id'),  # ideally, use request.user not this
                'rating': data.get('rating'),
                'review': data.get('review', ''),
            }
            file = None  # file upload can't be sent in JSON this way; handle separately if needed
            
            rating = create_rating(rating_data, file, request.user)
            data = {
                'id': rating.id,
                'review': rating.review,
                'photo': rating.photo_url.url if rating.photo_url else None,
                'created_by_fullname': f"{rating.user.first_name} {rating.user.last_name}",
                'created_at': rating.created_at.isoformat(),
                'rating': rating.rating,  # Add this key!
                'rating_range': list(range(rating.rating)),
                'empty_range': list(range(5 - rating.rating)),
            }
            print(data)
            return JsonResponse({'success': True, 'data': data})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
        
class RatingUpdateView(View,EnduserRequiredMixin):
    def get(self, request, pk):
        rating = get_rating_by_id(pk)
        if not rating:
            return redirect('rating_list')
        context = {'rating': rating}
        return render(request, 'rating/rating_update.html', context)

    def post(self, request, pk):
        rating = get_rating_by_id(pk)
        if not rating:
            return JsonResponse({'success': False, 'error': 'Rating not found'})
        data = request.POST.copy()
        try:
            update_data = {
                'product_id': data.get('product_id'),
                'photo_url': data.get('photo_url'),
                'user_id': data.get('user_id'),
                'rating': data.get('rating'),
                'review': data.get('review', ''),
            }
            update_data = {k: v for k, v in update_data.items() if v is not None}
            update_rating(rating, update_data)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

        
