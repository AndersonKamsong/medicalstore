from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.urls import reverse

from medicalstore.admin_site import admin_site


@admin.register(User, site=admin_site)
class CustomUserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'full_name',
        'is_active', 'is_staff', 'date_joined', 'order_count',
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    date_hierarchy = 'date_joined'
    list_per_page = 25

    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip() or '—'
    full_name.short_description = 'Full Name'

    def order_count(self, obj):
        from orders.models import Order
        count = Order.objects.filter(user=obj).count()
        url = reverse('admin:orders_order_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">{} order(s)</a>', url, count)
    order_count.short_description = 'Orders'


admin_site.register(Group, GroupAdmin)
