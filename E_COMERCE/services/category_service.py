from E_COMERCE.models import Category

def create_category(data,user):
    return Category.objects.create(
        name=data['name'],
        created_by = user,
        description=data['description'],
    )

def update_category(category_id, data):
    category = Category.objects.get(pk=category_id)
    category.name = data['name']
    category.description = data['description']
    category.save()
    return category

def get_category_data(category_id):
    return Category.objects.filter(id=category_id,is_active=True).first()

class CategoryNotFoundError(Exception):
    pass


def get_category_object(category_id):
    try:
        return Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        raise CategoryNotFoundError(f'Category with ID {category_id} not found')


def toggle_category_status(category_id, new_status: bool):
    category = get_category_object(category_id)
    category.is_active = new_status
    category.save()
    return category

def get_all_category():
    categories = Category.objects.all().order_by('id')
    category_data = []
    if categories:
        category_data = [
            {
              'id':category.id,
              'name':category.name,
              'description':category.description,
              'created_by':category.created_by,
              'created_at':category.created_at,
              'is_active' :category.is_active 
            }
            for category in categories
        ]
    return category_data

def get_categories():
    return Category.objects.all()