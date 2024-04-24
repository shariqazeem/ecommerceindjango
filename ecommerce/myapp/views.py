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

    cart_items = {product: cart_product_ids.count(product.id) for product in products_in_cart}
    cart_count = sum(cart_items.values())
    context = {'cart_items': cart_items, 'cart_count': cart_count}
    return render(request, 'cart.html', context)



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get the cart from the session or initialize it as an empty list
    cart = request.session.get('cart', [])
    
    cart = request.session.get('cart', [])

    cart.append(product_id)

    request.session['cart'] = cart
    
    return redirect('shopall')


# views.py

def update_cart_item(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            remove_from_cart(request, product_id)
        else:
            cart_items = request.session.get('cart', [])
            if product_id in cart_items:
                while product_id in cart_items:
                    cart_items.remove(product_id)
                cart_items.extend([product_id] * quantity)
                request.session['cart'] = cart_items
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart_items = request.session.get('cart', [])
    if product_id in cart_items:
        while product_id in cart_items:
            cart_items.remove(product_id)
        request.session['cart'] = cart_items
    return redirect('cart')

def get_cart_items(request):
    cart_items = request.session.get('cart', [])
    cart_item_count = {product_id: cart_items.count(product_id) for product_id in set(cart_items)}
    cart_products = Product.objects.filter(id__in=cart_item_count.keys())
    cart_items = {product: cart_item_count[product.id] for product in cart_products}
    return cart_items


def checkout(request):
    if request.method == 'POST':
        cart_items = get_cart_items(request)
        for product in cart_items:
            quantity = int(request.POST.get(f'quantity_{product.id}', 1))
            cart_items[product] = quantity
        request.session['cart'] = [product.id for product, quantity in cart_items.items() for _ in range(quantity)]

    cart_items = get_cart_items(request)
    subtotal = sum(product.price * quantity for product, quantity in cart_items.items())
    shipping_charge = 200
    total = subtotal + shipping_charge

    cart_count = sum(cart_items.values())
    return render(request, 'checkout.html', {'cart_items': cart_items, 'subtotal': subtotal, 'shipping_charge': shipping_charge, 'total': total, 'cart_count': cart_count})

def complete_order(request):
    return render(request, 'complete_order.html')