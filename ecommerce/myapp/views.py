from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order,Category,Brand
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
import paypalhttp
import paypalrestsdk
from paypalrestsdk import Payment


paypalrestsdk.configure({
    "mode": "sandbox",  # Change it to 'live' for production
    "client_id": "AXEE48s4gBY-C4JR6IGj6VAN2Pv0Y1MQym2Uij5sG7PZaO5_KDWirG5uu4fsx3Uzd8d8Yq9w9UNGoJcF",
    "client_secret": "ENp_zsOAUq8CH_0GWoYOSiSVTKr18uwv7kHH7uz-Yay1P2xbv-QCt-Mutb_BZ2m2PCiC_1KF6QyxuBnX"
})

def index(request):
    featured_products = Product.objects.filter(featured=True)
    main_products = Product.objects.filter(main_product=True)
    categories = Category.objects.all()  # Fetch all categories
    cart_count = calculate_cart_count(request)  # Add this line to get the cart count
    context = {
        'featured_products': featured_products,
        'main_products': main_products,
        'categories': categories,  # Pass categories to the template
        'cart_count': cart_count,  # Pass cart count to the template
    }
    return render(request, 'index.html', context)

def shopall(request):
    products = Product.objects.all()
    categories = Category.objects.all()  # Fetch all categories
    cart_count = calculate_cart_count(request)  # Add this line to get the cart count
    context = {
        'products': products,
        'categories': categories,  # Pass categories to the template
        'cart_count': cart_count,  # Pass cart count to the template
    }
    return render(request, 'shopall.html', context)

def category(request, category_name):
    category = Category.objects.get(name=category_name)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    cart_count = calculate_cart_count(request)  # Add this line to get the cart count
    return render(request, 'category.html', {'category': category, 'products': products, 'categories': categories, 'cart_count': cart_count})


@csrf_exempt
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()  # Fetch all categories
    cart_count = calculate_cart_count(request)  # Add this line to get the cart count
    context = {
        'product': product,
        'categories': categories,  # Pass categories to the template
        'cart_count': cart_count,  # Pass cart count to the template
    }
    return render(request, 'product_details.html', context)


def calculate_cart_count(request):
    cart_product_ids = request.session.get('cart', [])
    products_in_cart = Product.objects.filter(id__in=cart_product_ids)
    cart_items = {product: cart_product_ids.count(product.id) for product in products_in_cart}
    cart_count = sum(cart_items.values())
    return cart_count



@csrf_exempt
def cart(request):
    cart_product_ids = request.session.get('cart', [])
    products_in_cart = Product.objects.filter(id__in=cart_product_ids)
    categories = Category.objects.all()  # Fetch all categories
    cart_items = {product: cart_product_ids.count(product.id) for product in products_in_cart}
    cart_count = sum(cart_items.values())
    context = {'cart_items': cart_items, 'cart_count': cart_count,'categories':categories}
    return render(request, 'cart.html', context)

@csrf_exempt
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', [])
    cart.append(product_id)
    request.session['cart'] = cart
    
    # Check if there is a 'next' parameter in the request, and if so, redirect to that page
    next_page = request.GET.get('next')
    if next_page:
        return redirect(next_page)
    
    return redirect('shopall')

@csrf_exempt
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

@csrf_exempt
def remove_from_cart(request, product_id):
    cart_items = request.session.get('cart', [])
    if product_id in cart_items:
        while product_id in cart_items:
            cart_items.remove(product_id)
        request.session['cart'] = cart_items
    return redirect('cart')

@csrf_exempt
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

        subtotal = sum(product.price * quantity for product, quantity in cart_items.items())
        shipping_charge = 200
        total = subtotal + shipping_charge

        cart_count = sum(cart_items.values())

        payment_method = request.POST.get('payment_method')
        if payment_method == 'paypro':
            return render(request, 'paypal_payment.html', {'total': total})
        else:
            if payment_method:
                user, _ = User.objects.get_or_create(username='guest')
                order = Order.objects.create(
                    user=user,
                    full_name=request.POST.get('full_name'),
                    email=request.POST.get('email'),
                    country=request.POST.get('country'),
                    address=request.POST.get('address'),
                    city=request.POST.get('city'),
                    postal_code=request.POST.get('postal_code'),
                    phone_number=request.POST.get('phone_number'),
                    payment_method=payment_method,
                    total_bill=total
                )
                
                for product, quantity in cart_items.items():
                    order.order_items.create(product=product, quantity=quantity)
                
                del request.session['cart']
                
                if payment_method == 'paypro':
                    request.session['order_id'] = order.id
                    return redirect('paypal_payment')
                else:
                    messages.success(request, 'Your order has been completed successfully.')
                    return redirect('home')
            else:
                messages.error(request, 'Please select a payment method.')
                return redirect('checkout')

    cart_items = get_cart_items(request)
    subtotal = sum(product.price * quantity for product, quantity in cart_items.items())
    shipping_charge = 200
    total = subtotal + shipping_charge

    cart_count = sum(cart_items.values())
    return render(request, 'checkout.html', {'cart_items': cart_items, 'subtotal': subtotal, 'shipping_charge': shipping_charge, 'total': total, 'cart_count': cart_count})



def paypal_payment(request):
    order_id = request.session.get('order_id')
    order = Order.objects.get(id=order_id)
    cart_items = order.order_items.all()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_charge = 200
    total_bill = subtotal + shipping_charge

    paypal_order = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse("paypal_success")),
            "cancel_url": request.build_absolute_uri(reverse("paypal_cancel")),
        },
        "transactions": [{
            "amount": {
                "total": str(total_bill),
                "currency": "USD"
            },
            "description": "Payment for order #" + str(order_id)
        }]
    }

    request.session['paypal_order'] = paypal_order
    return redirect('paypal_redirect')

def paypal_redirect(request):
    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_CLIENT_SECRET
    paypal_sdk_client = paypalrestsdk.Api({
        "mode": "sandbox",  # Change it to 'live' for production
        "client_id": client_id,
        "client_secret": client_secret,
    })

    paypal_order = request.session['paypal_order']
    paypal_order["redirect_urls"] = {
        "return_url": request.build_absolute_uri(reverse("paypal_success")),
        "cancel_url": request.build_absolute_uri(reverse("paypal_cancel")),
    }

    payment = paypalrestsdk.Payment(paypal_order)
    if payment.create():
        for link in payment.links:
            if link.rel == 'approval_url':
                redirect_url = str(link.href)
                return redirect(redirect_url)
    else:
        messages.error(request, 'Payment processing failed. Please try again later.')
        return redirect('checkout')


def paypal_success(request):
    payer_id = request.GET.get('PayerID')
    order_id = request.session.get('order_id')
    
    paypal_sdk_client = paypalrestsdk.Api(
        {
            "mode": "sandbox",  # Change it to 'live' for production
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET,
        }
    )
    
    # Capture the payment status
    payment = paypalrestsdk.Payment.find(request.GET['paymentId'])
    if payment.execute({"payer_id": payer_id}):
        order = Order.objects.get(id=order_id)
        order.payment_status = "Paid"
        order.save()
        del request.session['order_id']
        del request.session['paypal_order']
        messages.success(request, 'Payment processed successfully.')
        return render(request, 'complete_order.html', {'order': order})
    else:
        messages.error(request, 'Payment processing failed. Please try again later.')
        return redirect('checkout')


def paypal_cancel(request):
    messages.error(request, 'Payment was cancelled.')
    return redirect('index')




@csrf_exempt
def complete_order(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        country = request.POST.get('country')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')
        
        cart_items = get_cart_items(request)
        subtotal = sum(product.price * quantity for product, quantity in cart_items.items())
        shipping_charge = 200
        total_bill = subtotal + shipping_charge
        
        user, _ = User.objects.get_or_create(username='guest')
        order = Order.objects.create(user=user, full_name=full_name, email=email, country=country, address=address, city=city, postal_code=postal_code, phone_number=phone_number, payment_method=payment_method, total_bill=total_bill)
        
        for product, quantity in cart_items.items():
            order.order_items.create(product=product, quantity=quantity)
        
        del request.session['cart']
        
        if payment_method == 'paypro':
            request.session['order_id'] = order.id
            return redirect('paypal_payment')
        else:
            messages.success(request, 'Your order has been completed successfully.')
        return render(request, 'complete_order.html', {'order': order})

    return render(request, 'complete_order.html')




