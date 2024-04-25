from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
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
    product = get_object_or_404(Product, id=product_id)
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
    cart = request.session.get('cart', [])
    cart.append(product_id)
    request.session['cart'] = cart
    return redirect('shopall')

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

from django.contrib.auth.models import User

def complete_order(request):
    if request.method == 'POST':
        # Process the order here
        # You can access shipping address and payment method from the POST data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        country = request.POST.get('country')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')
        
        # Create a temporary user
        user, _ = User.objects.get_or_create(username='guest')
        
        # Create a new order
        order = Order.objects.create(user=user, full_name=full_name, email=email, country=country, address=address, city=city, postal_code=postal_code, phone_number=phone_number, payment_method=payment_method)
        
        # Add items to the order
        cart_items = get_cart_items(request)
        for product, quantity in cart_items.items():
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
        
        # Clear the cart after completing the order
        del request.session['cart']
        
        messages.success(request, 'Your order has been completed successfully.')
        
        # Debugging: print out order details
        print("Order created successfully:")
        print("Shipping Address:", address)
        print("Payment Method:", payment_method)
        print("Ordered Items:")
        for item in OrderItem.objects.filter(order=order):
            print("-", item.quantity, "x", item.product.title)
        
        # Redirect to home page after 5 seconds
        return render(request, 'complete_order.html')

    # If the request method is GET, render the complete_order page
    return render(request, 'complete_order.html')
