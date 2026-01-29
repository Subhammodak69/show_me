from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import JsonResponse
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.services import product_info_service

class ItemInfoListView(AdminRequiredMixin, View):
    def get(self, request):
        items = product_info_service.get_all_iteminfos()
        return render(request, 'admin/iteminfo/iteminfo_list.html', {'iteminfos': items})

@method_decorator(csrf_exempt, name='dispatch')
class ItemInfoCreateView(AdminRequiredMixin, View):
    def get(self, request):
        productitems = product_info_service.get_active_products()
        sizes = product_info_service.get_size_choices_dict()
        colours = product_info_service.get_colour_choices_dict()
        return render(request, 'admin/iteminfo/iteminfo_create.html', {
            'productitems': productitems,
            'sizes': sizes,
            'colours': colours,
        })

    def post(self, request):
        try:
            file = request.FILES.get('photo')
            if not file:
                return JsonResponse({'success': False, 'error': 'Photo file is missing.'}, status=400)

            item = product_info_service.create_iteminfo(request, file)
            return JsonResponse({'success': True, 'id': item.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ItemInfoUpdateView(AdminRequiredMixin, View):
    def get(self, request, iteminfo_id):
        item = product_info_service.get_iteminfo_object(iteminfo_id)
        productitems = product_info_service.get_active_products()
        sizes = product_info_service.get_size_choices_dict()
        colours = product_info_service.get_colour_choices_dict()
        return render(request, 'admin/iteminfo/iteminfo_update.html', {
            'item': item,
            'productitems': productitems,
            'sizes': sizes,
            'colours': colours,
        })

    def post(self, request, iteminfo_id):
        try:
            data = request.POST
            file = request.FILES.get('photo')
            product_info_service.update_iteminfo(iteminfo_id, data, file)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class ItemInfoToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, iteminfo_id):
        try:
            new_status = product_info_service.toggle_iteminfo_status(iteminfo_id)
            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
