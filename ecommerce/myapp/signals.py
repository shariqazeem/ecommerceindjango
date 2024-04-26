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
