import csv
import json

from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from medicalstore.admin_site import admin_site
from pages.models import SiteSettings
from .email_utils import send_payment_details, send_status_update_email
from .models import Order, OrderItem

_STATUS_COLORS = {
    'pending': '#9E9E9E',
    'confirmed': '#2E7D32',
    'processing': '#2196F3',
    'shipped': '#FF9800',
    'delivered': '#4CAF50',
    'cancelled': '#F44336',
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total']
    fields = ['product', 'price', 'quantity', 'line_total']

    def line_total(self, obj):
        if obj.price is None or obj.quantity is None:
            return '€0.00'
        return f'€{obj.price * obj.quantity:.2f}'
    line_total.short_description = 'Line Total'


@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer_name', 'email', 'city',
        'status_badge', 'payment_method', 'total_amount',
        'item_count', 'created', 'payment_action',
    ]
    list_display_links = ['order_number']
    list_filter = ['status', 'payment_method', 'country', 'created', 'user']
    search_fields = ['first_name', 'last_name', 'email', 'city']
    readonly_fields = ['created', 'updated', 'total_amount']
    date_hierarchy = 'created'
    inlines = [OrderItemInline]
    actions = [
        'mark_confirmed', 'mark_processing', 'mark_shipped',
        'mark_delivered', 'mark_cancelled',
        'export_to_csv', 'send_payment_details_action',
    ]
    fieldsets = (
        ('Customer', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone'),
        }),
        ('Delivery Address', {
            'fields': ('address', 'postal_code', 'city', 'country'),
        }),
        ('Order', {
            'fields': ('status', 'payment_method', 'payment_status', 'total_amount'),
        }),
        ('Notes & Tracking', {
            'fields': ('notes',),
            'description': 'Internal notes, tracking numbers, and status history are logged here.',
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    # ── Custom URLs ────────────────────────────────────────────────────────────
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'send-payment-details/',
                self.admin_site.admin_view(self.send_payment_details_view),
                name='orders_order_send_payment_details',
            ),
        ]
        return custom + urls

    # ── List display helpers ───────────────────────────────────────────────────
    def order_number(self, obj):
        return f'ORD-{obj.id:05d}'
    order_number.short_description = 'Order #'
    order_number.admin_order_field = 'id'

    def customer_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    customer_name.short_description = 'Customer'

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def status_badge(self, obj):
        color = _STATUS_COLORS.get(obj.status, '#9E9E9E')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:500;">{}</span>',
            color, obj.get_status_display(),
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def payment_action(self, obj):
        url = reverse('admin:orders_order_send_payment_details') + f'?ids={obj.id}'
        return format_html(
            '<a href="{}" style="background:#2d5a27;color:#fff;padding:3px 10px;'
            'border-radius:4px;font-size:11px;text-decoration:none;white-space:nowrap;">💳 Pay</a>',
            url,
        )
    payment_action.short_description = 'Payment'

    # ── save_model: detect status change → log + send email 4 ─────────────────
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            try:
                original = Order.objects.get(pk=obj.pk)
                if original.status != obj.status:
                    ts = timezone.now().strftime('%Y-%m-%d %H:%M')
                    log = f'[{ts}] Status: {original.status} → {obj.status}\n'
                    obj.notes = log + (obj.notes or '')
                    send_status_update_email(obj)
                    self.message_user(
                        request,
                        f'Status update email sent to {obj.email}.',
                        level=messages.SUCCESS,
                    )
            except Exception as exc:
                self.message_user(request, f'Status email error: {exc}', level=messages.WARNING)
        super().save_model(request, obj, form, change)

    # ── Bulk status actions ────────────────────────────────────────────────────
    def _bulk_status(self, request, queryset, new_status):
        for order in queryset:
            old = order.status
            order.status = new_status
            ts = timezone.now().strftime('%Y-%m-%d %H:%M')
            order.notes = f'[{ts}] Status: {old} → {new_status}\n' + (order.notes or '')
            order.save(update_fields=['status', 'notes'])
            send_status_update_email(order)
        label = dict(Order.STATUS_CHOICES).get(new_status, new_status)
        self.message_user(request, f'{queryset.count()} order(s) marked as {label}.')

    @admin.action(description='Mark selected as Confirmed')
    def mark_confirmed(self, request, queryset):
        self._bulk_status(request, queryset, 'confirmed')

    @admin.action(description='Mark selected as Processing')
    def mark_processing(self, request, queryset):
        self._bulk_status(request, queryset, 'processing')

    @admin.action(description='Mark selected as Shipped')
    def mark_shipped(self, request, queryset):
        self._bulk_status(request, queryset, 'shipped')

    @admin.action(description='Mark selected as Delivered')
    def mark_delivered(self, request, queryset):
        self._bulk_status(request, queryset, 'delivered')

    @admin.action(description='Mark selected as Cancelled')
    def mark_cancelled(self, request, queryset):
        self._bulk_status(request, queryset, 'cancelled')

    # ── CSV export ─────────────────────────────────────────────────────────────
    @admin.action(description='Export selected orders to CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Order#', 'Date', 'Customer', 'Email', 'Phone',
            'Address', 'City', 'Country', 'Payment', 'Status', 'Total',
        ])
        for order in queryset:
            writer.writerow([
                f'ORD-{order.id:05d}',
                order.created.strftime('%Y-%m-%d %H:%M'),
                f'{order.first_name} {order.last_name}',
                order.email,
                order.phone,
                order.address,
                order.city,
                order.country,
                order.payment_method,
                order.status,
                order.total_amount,
            ])
        return response

    # ── Send payment details action (redirect to intermediate page) ────────────
    @admin.action(description='Send payment details to customer(s)')
    def send_payment_details_action(self, request, queryset):
        ids = ','.join(str(o.id) for o in queryset)
        url = reverse('admin:orders_order_send_payment_details')
        return HttpResponseRedirect(f'{url}?ids={ids}')

    # ── Send payment details view (GET = form, POST = send & redirect) ─────────
    def send_payment_details_view(self, request):
        ids_str = request.GET.get('ids') or request.POST.get('ids', '')
        try:
            ids = [int(i) for i in ids_str.split(',') if i.strip()]
        except ValueError:
            ids = []

        orders = Order.objects.filter(id__in=ids)
        if not orders.exists():
            messages.error(request, 'No orders selected.')
            return HttpResponseRedirect(reverse('admin:orders_order_changelist'))

        site = SiteSettings.get_settings()
        default_method = orders.first().payment_method if orders.count() == 1 else 'bank_transfer'

        if request.method == 'POST':
            method = request.POST.get('payment_method', 'bank_transfer')
            custom_message = request.POST.get('custom_message', '').strip()

            payment_info = {'payment_method': method}
            if method == 'bank_transfer':
                payment_info.update({
                    'bank_name': request.POST.get('bank_name', ''),
                    'bank_account_name': request.POST.get('bank_account_name', ''),
                    'bank_iban': request.POST.get('bank_iban', ''),
                    'bank_swift_bic': request.POST.get('bank_swift_bic', ''),
                })
            elif method == 'crypto':
                payment_info.update({
                    'coin_type': request.POST.get('coin_type', 'BTC'),
                    'wallet_address': request.POST.get('wallet_address', ''),
                })
            elif method == 'cod':
                payment_info['delivery_instructions'] = request.POST.get('delivery_instructions', '')

            sent, failed = 0, 0
            for order in orders:
                ok = send_payment_details(order, payment_info, custom_message)
                if ok:
                    # Mark confirmed + log
                    ts = timezone.now().strftime('%Y-%m-%d %H:%M')
                    order.notes = f'[{ts}] Payment details sent ({method})\n' + (order.notes or '')
                    order.status = 'confirmed'
                    order.save(update_fields=['status', 'notes'])
                    sent += 1
                else:
                    failed += 1

            if sent:
                messages.success(request, f'Payment details sent to {sent} customer(s). Orders marked Confirmed.')
            if failed:
                messages.error(request, f'Failed to send to {failed} customer(s). Check console logs.')
            return HttpResponseRedirect(reverse('admin:orders_order_changelist'))

        # Build JSON for the JS preview
        preview_orders_json = json.dumps([
            {
                'id_padded': f'{o.id:05d}',
                'first_name': o.first_name,
                'email': o.email,
                'total': str(o.total_amount),
            }
            for o in orders
        ])

        context = {
            **self.admin_site.each_context(request),
            'title': 'Send Payment Details',
            'orders': orders,
            'ids': ids_str,
            'site': site,
            'default_method': default_method,
            'preview_orders_json': preview_orders_json,
            'admin_email': request.user.email or site.email,
        }
        return TemplateResponse(request, 'admin/orders/send_payment_details.html', context)
