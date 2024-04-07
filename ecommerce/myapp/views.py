from django.shortcuts import render
from .models import Product
from django.http import JsonResponse


# Create your views here.
def index(request):
    featured_products = Product.objects.filter(featured=True)
    main_products = Product.objects.filter(main_product=True)

    context = {
        'featured_products': featured_products,
        'main_products': main_products

    }
    return render(request, 'index.html', context)

def shopall(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'shopall.html', context)

def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product
    }
    return render(request, 'product_details.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    # Get the cart from the session or create a new one if it doesn't exist
    cart = request.session.get('cart', {})
    
    # Increment the quantity if the product is already in the cart, otherwise set it to 1
    cart[product_id] = cart.get(product_id, 0) + 1

    # Update the session cart
    request.session['cart'] = cart

    return JsonResponse({'success': True})

def view_cart(request):
    # Get the cart from the session
    cart = request.session.get('cart', {})
    
    # Get product details for items in the cart
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})