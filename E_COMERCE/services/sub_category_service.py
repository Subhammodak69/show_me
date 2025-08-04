from E_COMERCE.models import SubCategory, Category

class SubCategoryNotFoundError(Exception):
    pass

def get_all_subcategories():
    return SubCategory.objects.select_related('category', 'created_by').all()

def get_subcategory_data(subcategory_id):
    try:
        return SubCategory.objects.get(pk=subcategory_id)
    except SubCategory.DoesNotExist:
        raise SubCategoryNotFoundError("Subcategory not found")

def get_all_categories():
    return Category.objects.filter(is_active=True)

def create_subcategory(data, user):
    category = Category.objects.get(pk=data['category_id'])
    return SubCategory.objects.create(
        name=data['name'],
        description=data['description'],
        category=category,
        created_by=user,
        is_active=data.get('is_active', True)
    )

def update_subcategory(subcategory_id, data):
    subcategory = get_subcategory_data(subcategory_id)
    subcategory.name = data['name']
    subcategory.description = data['description']
    subcategory.category = Category.objects.get(pk=data['category_id'])
    subcategory.is_active = data.get('is_active', subcategory.is_active)
    subcategory.save()
    return subcategory

def toggle_subcategory_status(subcategory_id, new_status):
    subcategory = get_subcategory_data(subcategory_id)
    subcategory.is_active = new_status
    subcategory.save()
    return subcategory

def get_subcategories():
    return SubCategory.objects.all()