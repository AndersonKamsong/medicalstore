import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from cart.cart import Cart
from pages.models import SiteSettings
from .forms import OrderCreateForm
from .models import Order, OrderItem


# ─── Email helpers ─────────────────────────────────────────────────────────────

def send_email_directly(subject, body, recipient_email, is_html=False):
    """Send a single email via SMTP_SSL using settings from environment."""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_EMAIL
        message["To"] = recipient_email
        message.attach(MIMEText(body, "html" if is_html else "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as server:
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Email error to {recipient_email}: {e}")
        return False


def send_admin_order_email(order, cleaned_data):
    """Notify admin of a new order."""
    subject = f'New Order #{order.id} — {order.total_amount}€'
    body = render_to_string('emails/admin_order_notification.html', {
        'order': order,
        'cleaned_data': cleaned_data,
        'payment_method': cleaned_data.get('payment_method', 'N/A'),
    })
    return send_email_directly(subject, body, settings.ADMIN_EMAIL, is_html=True)


def send_customer_order_confirmation(order, payment_method):
    """Send order confirmation to the customer. Includes bank details if payment is bank_transfer."""
    site_settings = SiteSettings.get_settings()
    subject = f'Order Confirmation #{order.id} — {site_settings.site_name}'
    body = render_to_string('emails/customer_order_confirmation.html', {
        'order': order,
        'payment_method': payment_method,
        'site_settings': site_settings,
    })
    return send_email_directly(subject, body, order.email, is_html=True)


# ─── Views ─────────────────────────────────────────────────────────────────────

def order_create(request):
    """Checkout: validate stock, create order, send emails."""
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    cart_items = cart.get_products_detail()

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():

            # ── Stock pre-check ───────────────────────────────────────────────
            for item in cart_items:
                product = item['product']
                if product.stock_quantity < item['quantity']:
                    messages.error(
                        request,
                        f'Sorry, only {product.stock_quantity} unit(s) of '
                        f'"{product.name}" are available. Please update your cart.'
                    )
                    return redirect('cart:cart_detail')

            # ── Create order ──────────────────────────────────────────────────
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
                    quantity=item['quantity'],
                )
                # Decrement stock
                item['product'].stock_quantity -= item['quantity']
                item['product'].save(update_fields=['stock_quantity'])

            cart.clear()
            messages.success(request, f'Order #{order.id} placed successfully!')

            # ── Emails ────────────────────────────────────────────────────────
            payment_method = form.cleaned_data.get('payment_method')
            send_customer_order_confirmation(order, payment_method)
            send_admin_order_email(order, form.cleaned_data)

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

    return render(request, 'orders/order/create.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price(),
        'total_quantity': len(cart),
        'form': form,
    })


def order_created(request, order_id):
    """Order confirmation page — only the order owner (or guest) may view it."""
    order = get_object_or_404(Order, id=order_id)
    if order.user is not None and request.user != order.user:
        return HttpResponseForbidden("You are not authorised to view this order.")
    return render(request, 'orders/order/created.html', {'order': order})


@login_required
def order_history(request):
    """Display the logged-in user's order history."""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order/history.html', {'orders': orders})
