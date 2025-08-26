from E_COMERCE.models import Offer
from E_COMERCE.models import Product

def get_all_offers():
    return Offer.objects.select_related('product').order_by('-created_at')

def get_offer_by_id(offer_id):
    try:
        return Offer.objects.get(id=offer_id)
    except Offer.DoesNotExist:
        return None

def create_offer(data):
    # Expects data as dict with relevant keys and validated values
    offer = Offer.objects.create(**data)
    return offer

def update_offer(offer, data):
    for field, value in data.items():
        setattr(offer, field, value)
    offer.save()
    return offer

def toggle_offer_status(offer, is_active):
    offer.is_active = is_active
    offer.save()
    return offer.is_active

def get_all_products():
    return Product.objects.all()
