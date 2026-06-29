from django.contrib import admin

from medicalstore.admin_site import admin_site
from .models import SiteSettings


@admin.register(SiteSettings, site=admin_site)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'tagline'),
            'description': 'Main site identification shown in the header and browser tab.',
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'address', 'business_hours'),
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',),
        }),
        ('Content', {
            'fields': ('about_text',),
            'classes': ('collapse',),
        }),
        ('Legal', {
            'fields': ('privacy_policy', 'terms_of_service'),
            'classes': ('collapse',),
        }),
        ('Bank Transfer Details', {
            'fields': (
                'bank_name', 'bank_account_name',
                'bank_account_number', 'bank_iban', 'bank_swift_bic',
            ),
            'description': (
                'Shown in order confirmation emails when customer selects bank transfer.'
            ),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if not SiteSettings.objects.exists():
            self.message_user(
                request,
                'No SiteSettings record exists yet. Click "Add Site Settings" to create one.',
                level='warning',
            )
        return super().changelist_view(request, extra_context)
