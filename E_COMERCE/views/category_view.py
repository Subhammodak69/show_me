from django.views import View
from django.http import JsonResponse
import json
from E_COMERCE.services import category_service
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin


class CategoryListView(AdminRequiredMixin,View):
    def get(self,request):
        category_data = category_service.get_all_category()
        return render(request, 'admin/category/category_list.html',{'category_data':category_data})


class CategoryCreateView(AdminRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin/category/category_create.html')

    def post(self, request):
        try:
            data = request.POST
            photo = request.FILES.get('photo')

            category = category_service.create_category(data, photo, request.user)
            return JsonResponse({'message': 'Category created successfully!', 'id': category.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class CategoryUpdateView(AdminRequiredMixin, View):
    def get(self, request, category_id):
        category = category_service.get_category_data(category_id)
        return render(request, 'admin/category/category_update.html', {'category': category})

    def post(self, request, category_id):  # <-- Use POST here!
        try:
            data = request.POST
            file = request.FILES.get('photo', None)
            category = category_service.update_category(category_id, data, file)
            return JsonResponse({'message': 'Category updated successfully!', 'id': category.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    
  

class ToggleCategoryStatusView(AdminRequiredMixin,View):

    def post(self, request, category_id):
        try:
            data = json.loads(request.body)
            new_status = data.get('is_active')

            if new_status is None:
                return JsonResponse({'success': False, 'error': 'Missing is_active value'}, status=400)

            category = category_service.toggle_category_status(category_id, new_status)
            return JsonResponse({'success': True, 'new_status': category.is_active})

        except category_service.CategoryNotFoundError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Something went wrong'}, status=500)