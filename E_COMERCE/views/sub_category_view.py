from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
import json
from E_COMERCE.services import sub_category_service
from E_COMERCE.constants.decorators import AdminRequiredMixin


class SubCategoryListView(AdminRequiredMixin,View):
    def get(self, request):
        subcategory_data = sub_category_service.get_all_subcategories()
        return render(request, 'admin/subcategory/subcategory_list.html', {'subcategory_data': subcategory_data})


class SubCategoryCreateView(AdminRequiredMixin,View):

    def get(self, request):
        categories = sub_category_service.get_all_categories()
        return render(request, 'admin/subcategory/subcategory_create.html', {'categories': categories})

    def post(self, request):
        try:
            data = json.loads(request.body)
            subcategory = sub_category_service.create_subcategory(data, request.user)
            return JsonResponse({'message': 'Subcategory created successfully!', 'id': subcategory.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class SubCategoryUpdateView(AdminRequiredMixin,View):

    def get(self, request, subcategory_id):
        subcategory = sub_category_service.get_subcategory_data(subcategory_id)
        categories = sub_category_service.get_all_categories()
        return render(request, 'admin/subcategory/subcategory_update.html', {'subcategory': subcategory, 'categories': categories})

    def put(self, request, subcategory_id):
        try:
            data = json.loads(request.body)
            subcategory = sub_category_service.update_subcategory(subcategory_id, data)
            return JsonResponse({'message': 'Subcategory updated successfully!', 'id': subcategory.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ToggleSubCategoryStatusView(AdminRequiredMixin,View):

    def post(self, request, subcategory_id):
        try:
            data = json.loads(request.body)
            new_status = data.get('is_active')

            if new_status is None:
                return JsonResponse({'success': False, 'error': 'Missing is_active value'}, status=400)

            subcategory = sub_category_service.toggle_subcategory_status(subcategory_id, new_status)
            return JsonResponse({'success': True, 'new_status': subcategory.is_active})

        except sub_category_service.SubCategoryNotFoundError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        except Exception:
            return JsonResponse({'success': False, 'error': 'Something went wrong'}, status=500)

    