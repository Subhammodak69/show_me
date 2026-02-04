from E_COMERCE.models import Product,ProductItem
from django.core.exceptions import ObjectDoesNotExist
from E_COMERCE.constants.default_values import Size,Color
from django.http import JsonResponse

def get_all_products():
    return Product.objects.select_related('subcategory').all()

def get_product_object_by_id(product_id):
    return Product.objects.filter(id=product_id,is_active=True).first()

def get_product_by_id(product_id):
    return Product.objects.get(id=product_id)

def create_product(data):
    try:
        return Product.objects.create(
            name=data['name'],
            description=data['description'],
            subcategory_id=data['subcategory_id'],
        )
    except Exception as e:
        raise Exception(f"Product creation failed: {e}")

def update_product(product_id, data):
    try:
        product = Product.objects.get(id=product_id)
        product.name = data['name']
        product.description = data['description']
        product.subcategory_id = data['subcategory_id']
        product.save()
        return product
    except ObjectDoesNotExist:
        raise Exception("Product not found.")
    except Exception as e:
        raise Exception(f"Product update failed: {e}")

def get_all_product_items():
    product_items = ProductItem.objects.select_related('product').filter(
        is_active=True, product__is_active=True
    )

    data = []

    for item in product_items:
        data.append({
            'id': item.id,
            'price': item.price,
            'photo_url': item.photo_url,
            'size': Size(item.size).name if item.size in [s.value for s in Size] else "UNKNOWN",
            'color': Color(item.color).name if item.color in [c.value for c in Color] else "UNKNOWN",
            'product': item.product,
            'is_active': item.is_active,
        })

    return data


def get_product_items_by_product(product_id):
    items = ProductItem.objects.filter(product_id=product_id, is_active=True).select_related('product')
    
    response = []
    for item in items:
        response.append({
            'id': item.id,
            'size': Size(item.size).name if item.size in [s.value for s in Size] else "UNKNOWN",
            'color': Color(item.color).name if item.color in [c.value for c in Color] else "UNKNOWN",
            'price': item.price
        })
    
    return response


def category_product_search(request):
    query = request.GET.get("q", "").strip()
    productitems = []
    if query == "":
        productitems = []
        
    else:
        productitems = ProductItem.objects.filter(
            product__name__icontains=query,
            is_active=True
        )
    # print(f"Found {productitems.count()} items")  # log result count

    results = [{
        "id": item.id,
        "product_name": item.product.name,
        "price": item.price,
        "photo_url": item.photo_url,
    } for item in productitems]
    # print(results)
    return JsonResponse(results, safe=False)