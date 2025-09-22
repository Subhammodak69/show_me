from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from E_COMERCE.services import poster_service
from E_COMERCE.models import Poster
from E_COMERCE.models import User
from E_COMERCE.constants.decorators import AdminRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class PosterListView(AdminRequiredMixin,View):
    def get(self,request):
        posters = poster_service.get_all_posters()
        return render(request,'admin/poster/poster_list.html',{'posters':posters})


@method_decorator(csrf_exempt, name='dispatch')
class AdminPosterCreateView(AdminRequiredMixin, View):
    def get(self, request):
        users = User.objects.all()
        return render(request, 'admin/poster/poster_create.html', {'users': users})

    def post(self, request):
        try:
            data = {
                'user_id': request.user.id,
                'title': request.POST.get('title', ''),
                'description': request.POST.get('description', ''),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
            }
            file = request.FILES.get('photo')
            poster = poster_service.create_poster(data, file)
            return JsonResponse({'success': True, 'id': poster.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class AdminPosterUpdateView(AdminRequiredMixin, View):
    def get(self, request, poster_id):
        users = User.objects.all()
        poster = Poster.objects.get(id=poster_id)
        return render(request, 'admin/poster/poster_update.html', {'users': users, 'poster': poster})

    def post(self, request, poster_id):
        try:
            data = {
                'user_id': request.user.id,
                'title': request.POST.get('title', ''),
                'description': request.POST.get('description', ''),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
            }
            file = request.FILES.get('photo')
            poster_service.update_poster(poster_id, data, file)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class AdminPosterToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, poster_id):
        try:
            new_status = poster_service.toggle_poster_status(poster_id)
            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
