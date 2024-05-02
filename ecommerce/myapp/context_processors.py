# myapp/context_processors.py
from .models import Brand, Caraousel

def brand_logo(request):
    brand_logo_url = None
    brand = Brand.objects.first()
    if brand:
        brand_logo_url = brand.logo.url
    return {'brand_logo': brand_logo_url}

def carousel_info(request):
    carousel_data = Caraousel.objects.first()
    return {
        'carousel_brand_name': carousel_data.brand_name if carousel_data else None,
        'carousel_description': carousel_data.description if carousel_data else None,
        'carousel_image': carousel_data.image.url if carousel_data else None,
    }