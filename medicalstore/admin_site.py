from django.contrib.admin import AdminSite


class MedicalStoreAdminSite(AdminSite):
    site_header = 'MedicalStore Admin'
    site_title = 'MedicalStore'
    index_title = 'Dashboard'

    def index(self, request, extra_context=None):
        from products.models import Product, Category
        from orders.models import Order
        from django.contrib.auth.models import User
        from django.db.models import Sum

        extra_context = extra_context or {}

        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        low_stock = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=10).count()

        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        revenue = Order.objects.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        registered_users = User.objects.count()
        recent_orders = Order.objects.select_related('user').order_by('-created')[:10]
        low_stock_products = (
            Product.objects.select_related('category')
            .filter(is_active=True)
            .order_by('stock_quantity')[:10]
        )

        extra_context.update({
            'stat_total_products': total_products,
            'stat_active_products': active_products,
            'stat_inactive_products': total_products - active_products,
            'stat_total_categories': total_categories,
            'stat_total_orders': total_orders,
            'stat_pending_orders': pending_orders,
            'stat_revenue': revenue,
            'stat_low_stock': low_stock,
            'stat_out_of_stock': out_of_stock,
            'stat_registered_users': registered_users,
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
        })

        return super().index(request, extra_context)


admin_site = MedicalStoreAdminSite(name='admin')
