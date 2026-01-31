from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from E_COMERCE.services.rating_service import *
from E_COMERCE.constants.decorators import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class RatingCreateView(View, EnduserRequiredMixin):
    def post(self, request):
        try:
            # print("helllooo")
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
            # print(data)
            return JsonResponse({'success': True, 'data': data})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

@method_decorator(csrf_exempt, name='dispatch')
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
        

        
#admin

class AdminReviewListView(AdminRequiredMixin,View):
    def get(self,request):
        reviews_data = get_all_reviews_for_admin()
        return render(request,'admin/review/review_list.html',{'reviews':reviews_data})
    
class AdminReviewCreateView(AdminRequiredMixin,View):
    def get(self,request):
        return
    
class AdminReviewUpdateView(AdminRequiredMixin,View):
    def get(self,request):
        return
    
@method_decorator(csrf_exempt, name='dispatch')
class AdminreviewToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, review_id):
        try:
            body = json.loads(request.body)
            is_active = body.get('is_active')

            new_status = toggle_review_active_status(review_id, is_active)

            return JsonResponse({'success': True, 'new_status': new_status})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception:
            return JsonResponse({'success': False, 'error': 'Something went wrong'})
        