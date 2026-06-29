"""
Email utility functions for order-related notifications.

All functions:
- Use Django's email backend (console in dev, SMTP in production)
- Wrap in try/except so email failures never crash the order flow
- Print result to console for easy debugging
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from pages.models import SiteSettings


def _send(subject, html_body, to_email):
    """Send an HTML email via the configured Django email backend."""
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        print(f'Email sent: "{subject}" → {to_email}')
        return True
    except Exception as exc:
        print(f'Email failed: "{subject}" → {to_email} — {exc}')
        return False


# ─── Email 1: Customer Order Received ──────────────────────────────────────────

def send_order_received_customer(order):
    """Thank-you email sent to the customer immediately after order placement."""
    site = SiteSettings.get_settings()
    subject = f'Order Received – ORD-{order.id:05d} | {site.site_name}'
    html = render_to_string('emails/order_received_customer.html', {
        'order': order,
        'site': site,
        'items': order.items.select_related('product').all(),
    })
    return _send(subject, html, order.email)


# ─── Email 2: Admin New Order Notification ─────────────────────────────────────

def send_order_received_admin(order):
    """Internal alert sent to ADMIN_EMAIL when a new order is placed."""
    site = SiteSettings.get_settings()
    subject = f'NEW ORDER – ORD-{order.id:05d} from {order.first_name} {order.last_name}'
    html = render_to_string('emails/order_received_admin.html', {
        'order': order,
        'site': site,
        'items': order.items.select_related('product').all(),
        'admin_order_url': f'/admin/orders/order/{order.id}/change/',
    })
    return _send(subject, html, settings.ADMIN_EMAIL)


# ─── Email 3: Payment Details (sent manually from admin) ───────────────────────

def send_payment_details(order, payment_info, custom_message=''):
    """
    Send payment instructions to the customer.

    payment_info dict keys vary by payment method:
      bank_transfer: bank_name, bank_account_name, bank_iban, bank_swift_bic
      crypto:        coin_type, wallet_address
      cod:           delivery_instructions
    """
    site = SiteSettings.get_settings()
    subject = f'Payment Details – ORD-{order.id:05d} | {site.site_name}'
    html = render_to_string('emails/payment_details.html', {
        'order': order,
        'site': site,
        'payment_info': payment_info,
        'custom_message': custom_message,
        'admin_email': settings.ADMIN_EMAIL,
    })
    return _send(subject, html, order.email)


# ─── Email 4: Order Status Update ──────────────────────────────────────────────

_STATUS_INFO = {
    'confirmed': {
        'message': 'Your order has been confirmed and is being prepared.',
        'color': '#2d5a27',
        'icon': '✅',
    },
    'processing': {
        'message': 'Your order is currently being processed.',
        'color': '#1565c0',
        'icon': '⚙️',
    },
    'shipped': {
        'message': 'Great news! Your order has been shipped and is on its way.',
        'color': '#e65100',
        'icon': '🚚',
    },
    'delivered': {
        'message': 'Your order has been delivered. Thank you for your purchase!',
        'color': '#2d5a27',
        'icon': '🎉',
    },
    'cancelled': {
        'message': (
            'Unfortunately your order has been cancelled. '
            'Please contact us if you have any questions.'
        ),
        'color': '#c62828',
        'icon': '❌',
    },
}


def send_status_update_email(order):
    """Notify the customer whenever the order status changes to a notifiable state."""
    info = _STATUS_INFO.get(order.status)
    if not info:
        return False  # no email for 'pending' or unknown statuses

    site = SiteSettings.get_settings()
    subject = f'Order Update – ORD-{order.id:05d} is now {order.get_status_display()} | {site.site_name}'
    html = render_to_string('emails/order_status_update.html', {
        'order': order,
        'site': site,
        'status_message': info['message'],
        'header_color': info['color'],
        'status_icon': info['icon'],
    })
    return _send(subject, html, order.email)
