from django.shortcuts import render,redirect,get_object_or_404
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

def cart(request):
    cart_product_ids = request.session.get('cart', [])
    products_in_cart = Product.objects.filter(id__in=cart_product_ids)
    context = {'cart_items': products_in_cart}
    return render(request, 'cart.html', context)



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get the cart from the session or initialize it as an empty list
    cart = request.session.get('cart', [])
    
    # Check if the product is already in the cart
    if product.id not in cart:
        # Add the product ID to the cart
        cart.append(product.id)
        
        # Update the session with the new cart data
        request.session['cart'] = cart
        
        # Update cart count in session
        request.session['cart_count'] = len(cart)
    
    return redirect('shopall')


# views.py

def update_cart_item(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            remove_from_cart(request, product_id)
        else:
            cart_items = request.session.get('cart', {})
            if product_id in cart_items:
                cart_items[product_id] = quantity
                request.session['cart'] = cart_items
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart_items = request.session.get('cart', [])
    if product_id in cart_items:
        cart_items.remove(product_id)
        request.session['cart'] = cart_items
        
        # Update cart count in session
        request.session['cart_count'] = len(cart_items)
        
    return redirect('cart')


def checkout(request):
    return render(request, 'checkout.html')
