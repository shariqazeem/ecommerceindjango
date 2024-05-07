from django.contrib import messages
import os
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order,Category,Brand
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
import paypalrestsdk
from paypalrestsdk import Payment
from django.core.mail import send_mail
from decimal import Decimal

paypalrestsdk.configure({
    "mode": "sandbox",  # Change it to 'live' for production
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

def send_store_notification(order):
    subject = 'New Order Received'
    order_items = order.order_items.all()  # Use the related name specified in the OrderItem model
    products = [f"{item.product.title} (Quantity: {item.quantity})" for item in order_items]
    total_bill = order.total_bill

    message = f'''
    Hi,

    You have received a new order:

    Order ID: {order.id}
    Products: {", ".join(products)}
    Amount: {total_bill}
    Shipping Address: {order.address}, {order.city}, {order.country}, {order.postal_code}
    Payment Method: {order.get_payment_method_display()}
    Phone Number: {order.phone_number}

    Regards,
    Shariq Traders
    '''
    from_email = 'shariqshaukat786@gmail.com'
    to_email = [from_email]  # Send email to the store owner

    send_mail(subject, message, from_email, to_email)

def send_customer_notification(order):
    subject = 'Thank You for Your Order'
    order_items = order.order_items.all()
    total_bill = order.total_bill

    # Constructing HTML email message using Django template syntax
    message = '''
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }}
                .container {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 20px;
                }}
                .header {{
                    background-color: #f4f4f4;
                    border-bottom: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                .order-details {{
                    margin-top: 20px;
                }}
                .thank-you {{
                    margin-top: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Thank You for Your Order!</h2>
                </div>
                <div class="order-details">
                    <p>Hi {full_name},</p>
                    <p>We have received your order with the following details:</p>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Products:</strong></p>
                    <ul>
                        {items}
                    </ul>
                    <p><strong>Total Amount:</strong> PKR{total_bill}</p>
                    <p><strong>Payment Method:</strong> {payment_method}</p>
                </div>
                <div class="thank-you">
                    <p>We will update you soon with the status of your order.</p>
                    <p>Regards,<br>Shariq Traders</p>
                </div>
            </div>
        </body>
    </html>
    '''.format(
        full_name=order.full_name,
        order_id=order.id,
        items=''.join(f'<li>{item.product.title} (Quantity: {item.quantity})</li>' for item in order_items),
        total_bill=total_bill,
        payment_method=order.get_payment_method_display()
    )

    from_email = 'shariqshaukat786@gmail.com'
    to_email = [order.email]

    send_mail(subject, '', from_email, to_email, html_message=message)



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

        payment_method = request.POST.get('payment_method')
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
                request.session['order_id'] = order.id  # Set order_id in session
                return redirect('paypal_payment')
            else:
                request.session['order_id'] = order.id  # Set order_id in session
                messages.success(request, 'Your order has been completed successfully.')
                return redirect('complete_order')
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



@csrf_exempt
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
        
        # Send email to the store owner
        send_store_notification(order)
        # Send email to the customer
        send_customer_notification(order)
        
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
        order = Order.objects.create(
            user=user, 
            full_name=full_name, 
            email=email, 
            country=country, 
            address=address, 
            city=city, 
            postal_code=postal_code, 
            phone_number=phone_number, 
            payment_method=payment_method, 
            total_bill=float(total_bill)
        )
        
        for product, quantity in cart_items.items():
            order.order_items.create(product=product, quantity=quantity)
        
        del request.session['cart']

        if payment_method == 'paypro':
            request.session['order_id'] = order.id

            # PayPal payment process
            request.session['payment_method'] = payment_method
            request.session['full_name'] = full_name
            request.session['email'] = email
            request.session['country'] = country
            request.session['address'] = address
            request.session['city'] = city
            request.session['postal_code'] = postal_code
            request.session['phone_number'] = phone_number
            request.session['total_bill'] = float(total_bill)
            
            return redirect('paypal_payment')
        else:
            # Cash on Delivery
            messages.success(request, 'Your order has been completed successfully.')
            # Send email to the store owner
            send_store_notification(order)
            # Send email to the customer
            send_customer_notification(order)
            return render(request, 'complete_order.html', {'order': order})

    return render(request, 'complete_order.html')
