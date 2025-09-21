from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from .models import OrderItem, Order
from .forms import OrderCreateForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from .models import Order, OrderItem
from cart.cart import Cart
from .forms import OrderCreateForm

def send_email_directly(subject, body, recipient_email, is_html=False):
    """Send email directly using SMTP_SSL (bypassing Django's email backend)"""
    try:
        sender_email = settings.SMTP_EMAIL
        password = settings.SMTP_PASSWORD
        host = settings.SMTP_HOST
        port = settings.SMTP_PORT
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        
        if is_html:
            # For HTML emails
            part = MIMEText(body, "html")
        else:
            # For plain text emails
            part = MIMEText(body, "plain")
        
        message.attach(part)
        
        # Create secure SSL context
        context = ssl.create_default_context()
        
        # Send email
        with smtplib.SMTP_SSL("smtp.hostinger.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"✓ Email sent successfully to {recipient_email}!")
            return True
            
    except Exception as e:
        print(f"✗ Email sending error to {recipient_email}: {e}")
        return False

def send_admin_order_email(order, cleaned_data):
    """Send order confirmation email to admin using direct SMTP"""
    admin_email = settings.ADMIN_EMAIL
    
    subject = f'🛒 New Order #{order.id} - {order.total_amount}€'
    body = render_to_string('emails/admin_order_notification.html', {
        'order': order,
        'cleaned_data': cleaned_data,
        'payment_method': cleaned_data.get('payment_method', 'N/A')
    })
    
    # Use direct SMTP instead of Django's EmailMessage
    return send_email_directly(subject, body, admin_email, is_html=True)

@csrf_exempt
def order_create(request):
    """Create a new order and handle bank payment email if needed"""
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    cart_items = cart.get_products_detail()

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_amount = cart.get_total_price()
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            cart.clear()
            messages.success(request, f'Order {order.id} created successfully!')

            # Send bank info email if payment method is bank
            payment_method = form.cleaned_data.get('payment_method')
            customer_email = form.cleaned_data.get('email')
            
            if payment_method == 'bank_transfer' and customer_email:
                subject = f'🌿 Green Houses CBD - Instructions for Bank Transfer (Order #{order.id})'
                body = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                        <div style="background-color: #f5f9f0; padding: 20px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                        <h1 style="color: #2E7D32; margin-top: 0;">Thank You for Your Order #{order.id}</h1>
                        <p>Dear Valued Customer,</p>
                        <p>We appreciate your trust in Green Houses CBD. Please find below the details for your bank transfer payment:</p>
                        </div>

                        <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h2 style="color: #2E7D32; margin-top: 0;">💰 Payment Instructions</h2>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                            <td style="padding: 8px 0; width: 120px; font-weight: bold;">Bank Name:</td>
                            <td style="padding: 8px 0;">ABC Bank</td>
                            </tr>
                            <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Account Name:</td>
                            <td style="padding: 8px 0;">Green Houses CBD</td>
                            </tr>
                            <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Account Number:</td>
                            <td style="padding: 8px 0;">123456789</td>
                            </tr>
                            <tr>
                            <td style="padding: 8px 0; font-weight: bold;">IBAN:</td>
                            <td style="padding: 8px 0;">FR76 3000 6000 0112 3456 7890 189</td>
                            </tr>
                            <tr>
                            <td style="padding: 8px 0; font-weight: bold;">SWIFT/BIC:</td>
                            <td style="padding: 8px 0;">AGRIFRPPXXX</td>
                            </tr>
                            <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Amount Due:</td>
                            <td style="padding: 8px 0; font-weight: bold; color: #2E7D32;">€{order.total_amount}</td>
                            </tr>
                        </table>
                        
                        <p style="background-color: #fff8e1; padding: 12px; border-left: 4px solid #ffc107; margin: 15px 0;">
                            <strong>⚠️ Important:</strong> Please include your Order ID <strong>#{order.id}</strong> in the payment reference to ensure prompt processing.
                        </p>
                        </div>

                        <div style="margin: 20px 0;">
                        <h3 style="color: #2E7D32;">Next Steps</h3>
                        <ol style="padding-left: 20px;">
                            <li style="margin-bottom: 8px;">Complete your bank transfer using the details above</li>
                            <li style="margin-bottom: 8px;">Keep your transaction receipt for reference</li>
                            <li style="margin-bottom: 8px;">We'll notify you once payment is received</li>
                            <li>Your order will be prepared for shipment</li>
                        </ol>
                        </div>

                        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <p>Need assistance? Contact our friendly support team:</p>
                        <p style="margin: 10px 0;">
                            <a href="mailto:support@greenmedstore.com" style="color: #2E7D32; text-decoration: none; font-weight: bold;">support@greenmedstore.com</a>
                        </p>
                        <p style="margin: 0;">
                            <a href="https://www.greenmedstore.com" style="color: #2E7D32; text-decoration: none;">www.greenmedstore.com</a>
                        </p>
                        </div>

                        <p style="color: #666; font-size: 0.9em; border-top: 1px solid #eee; padding-top: 15px;">
                        With green regards,<br>
                        <strong>The Green Houses CBD Team</strong><br>
                        <span style="color: #4CAF50;">Nurturing Your Wellness Naturally</span>
                        </p>
                    </body>
                    </html>
                    """
                
                # Use direct SMTP instead of Django's EmailMessage
                email_sent = send_email_directly(subject, body, customer_email, is_html=True)
                if email_sent:
                    messages.info(request, f'Bank transfer instructions sent to {customer_email}')
                else:
                    messages.warning(request, 'Failed to send bank instructions email. Please contact support.')

            # 2. Send admin email notification
            admin_email_sent = send_admin_order_email(order, form.cleaned_data)
            # if not admin_email_sent:
                # messages.warning(request, 'Failed to send admin notification. Please check admin email settings.')
            
            return redirect('orders:order_created', order_id=order.id)

    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price(),
        'total_quantity': len(cart),
        'form': form,
    }

    return render(request, 'orders/order/create.html', context)

def order_created(request, order_id):
    """Order confirmation page"""
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order/created.html', {'order': order})


@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order/history.html', {'orders': orders})
