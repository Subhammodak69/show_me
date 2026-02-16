from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import render
from E_COMERCE.constants.decorators import AdminRequiredMixin
from E_COMERCE.services import product_image_service,productitem_service

class AdminProductimageListView(AdminRequiredMixin, View):
    def get(self, request):
        images = product_image_service.get_all_images()
        product_items = productitem_service.get_all_productitems()
        return render(request, 'admin/product_image/product_image_list.html', {
            'images': images,
            'product_items': product_items
        })

@method_decorator(csrf_exempt, name='dispatch')
class AdminProductimageCreateView(AdminRequiredMixin, View):
    def get(self, request):
        product_items = productitem_service.get_all_productitems()
        return render(request, 'admin/product_image/product_image_create.html', {'product_items': product_items})

    def post(self, request):
        try:
            data = {
                'product_item_id': request.POST.get('product_item'),
                'is_active': request.POST.get('is_active') == 'on'
            }
            file = request.FILES.get('photo')
            image = product_image_service.create_image(data, file)
            return JsonResponse({'success': True, 'id': image.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class AdminProductimageUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        product_items = productitem_service.get_all_productitems()
        image = product_image_service.get_all_images()
        return render(request, 'admin/product_image/product_image_update.html', {
            'product_items': product_items, 
            'image': image
        })

    def post(self, request, pk):
        try:
            data = {
                'product_item_id': request.POST.get('product_item'),
                'is_active': request.POST.get('is_active') == 'on'
            }
            file = request.FILES.get('photo')
            product_image_service.update_image(pk, data, file)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class AdminProductimageToggleStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            new_status = product_image_service.toggle_image_status(pk)
            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class ApiExtraProductImagesView(View):
    def get(self, request,product_item_id):
        try:
            extra_product_images = product_image_service.get_extra_product_images(product_item_id) 
            return JsonResponse({
                'success': True, 
                'extra_product_images': extra_product_images
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })