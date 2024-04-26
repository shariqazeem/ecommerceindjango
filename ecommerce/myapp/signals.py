from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(post_save, sender=OrderItem)
def order_notification(sender, instance, created, **kwargs):
    if created:
        order = instance.order  # Get the order related to the OrderItem
        # Send email to the store owner
        send_store_notification(order)
        # Send email to the customer
        send_customer_notification(order)

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
    order_items = order.order_items.all()  # Use the related name specified in the OrderItem model
    products = [f"{item.product.title} (Quantity: {item.quantity})" for item in order_items]
    total_bill = order.total_bill

    message = f'''
    Hi {order.full_name},

    Thank you for your order. We have received your order:

    Order ID: {order.id}
    Products: {", ".join(products)}
    Amount: {total_bill}
    Payment Method: {order.get_payment_method_display()}

    We will update you soon with the status of your order.

    Regards,
    Shariq Traders
    '''
    from_email = 'shariqshaukat786@gmail.com'
    to_email = [order.email]  # Send email to the customer

    send_mail(subject, message, from_email, to_email)
