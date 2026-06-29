from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart
from .email_utils import send_order_received_admin, send_order_received_customer
from .forms import OrderCreateForm
from .models import Order, OrderItem


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
                item['product'].stock_quantity -= item['quantity']
                item['product'].save(update_fields=['stock_quantity'])

            cart.clear()
            messages.success(request, f'Order #{order.id} placed successfully!')

            # ── Emails (Email 1 + Email 2) ───────────────────────────────────
            send_order_received_customer(order)
            send_order_received_admin(order)

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
