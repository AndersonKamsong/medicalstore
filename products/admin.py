from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import ImageField

from medicalstore.admin_site import admin_site
from .models import Category, Product
from .widgets import CloudinaryImageWidget



class StockStatusFilter(admin.SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return [
            ('out', 'Out of Stock (0)'),
            ('low', 'Low Stock (1–10)'),
            ('ok', 'In Stock (>10)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'out':
            return queryset.filter(stock_quantity=0)
        if self.value() == 'low':
            return queryset.filter(stock_quantity__gt=0, stock_quantity__lte=10)
        if self.value() == 'ok':
            return queryset.filter(stock_quantity__gt=10)
        return queryset


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'slug', 'strain_type', 'product_count', 'created_at']
    list_filter = ['strain_type', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    formfield_overrides = {ImageField: {'widget': CloudinaryImageWidget}}

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'image', 'image_preview', 'strain_type',
                       'preferred_ratio', 'icon', 'is_medical', 'is_recreational'),
        }),
        ('Medical Info', {
            'fields': ('primary_benefits', 'dosage_advice', 'effects_timeline',
                       'storage_advice', 'recommended_methods'),
            'classes': ('collapse',),
        }),
        ('SEO', {
            'fields': ('description', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;" />',
                    obj.image.url,
                )
            except Exception:
                return '—'
        return '—'
    image_preview.short_description = 'Preview'

    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:products_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    product_count.short_description = 'Products'


@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'name', 'category', 'price',
        'stock_quantity', 'stock_badge', 'is_active', 'featured', 'created_at',
    ]
    list_display_links = ['name']
    list_editable = ['price', 'stock_quantity', 'is_active', 'featured']
    list_filter = ['category', 'is_active', 'featured', 'strain_type', StockStatusFilter, 'created_at']
    search_fields = ['name', 'description', 'composition']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview', 'created_at', 'updated_at', 'average_rating', 'rating_count']
    date_hierarchy = 'created_at'
    list_per_page = 20
    actions = ['mark_active', 'mark_inactive', 'mark_featured', 'unmark_featured']
    formfield_overrides = {ImageField: {'widget': CloudinaryImageWidget}}

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'category', 'image', 'image_preview',
                       'is_active', 'featured', 'strain_type', 'preferred_ratio', 'recommended_methods'),
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity'),
        }),
        ('Description & Details', {
            'fields': ('description', 'composition', 'usage_instructions',
                       'creation_method', 'benefits'),
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Ratings', {
            'fields': ('average_rating', 'rating_count'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            try:
                url = obj.image.url
                is_cloud = 'cloudinary.com' in url
                bg = '#4CAF50' if is_cloud else '#FF9800'
                icon = '&#9729;' if is_cloud else '&#9888;'
                return format_html(
                    '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;" />'
                    '<br><span style="font-size:10px;background:{};color:white;'
                    'padding:1px 5px;border-radius:8px;">{}</span>',
                    url, bg, icon,
                )
            except Exception:
                return '—'
        return '—'
    image_preview.short_description = 'Image'

    def stock_badge(self, obj):
        if obj.stock_quantity == 0:
            bg, label = '#F44336', 'Out of Stock'
        elif obj.stock_quantity <= 10:
            bg, label = '#FF9800', f'Low ({obj.stock_quantity})'
        else:
            bg, label = '#4CAF50', f'In Stock ({obj.stock_quantity})'
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:12px;font-size:12px;white-space:nowrap;">{}</span>',
            bg, label,
        )
    stock_badge.short_description = 'Stock'

    @admin.action(description='Mark selected as active')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Mark selected as inactive')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Mark selected as featured')
    def mark_featured(self, request, queryset):
        queryset.update(featured=True)

    @admin.action(description='Remove featured from selected')
    def unmark_featured(self, request, queryset):
        queryset.update(featured=False)
