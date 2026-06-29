import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from medicalstore.admin_site import admin_site
from .models import Order, OrderItem

_STATUS_COLORS = {
    'pending': '#9E9E9E',
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
        return f'€{obj.price * obj.quantity:.2f}'
    line_total.short_description = 'Line Total'


@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer_name', 'email', 'city',
        'status_badge', 'payment_method', 'total_amount', 'item_count', 'created',
    ]
    list_display_links = ['order_number']
    list_filter = ['status', 'payment_method', 'country', 'created', 'user']
    search_fields = ['first_name', 'last_name', 'email', 'city']
    readonly_fields = ['created', 'updated', 'total_amount']
    date_hierarchy = 'created'
    inlines = [OrderItemInline]
    actions = ['mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled', 'export_to_csv']

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

    @admin.action(description='Mark selected as Processing')
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')

    @admin.action(description='Mark selected as Shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description='Mark selected as Delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description='Mark selected as Cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

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
