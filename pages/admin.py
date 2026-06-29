from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'tagline', 'about_text')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'business_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Legal', {
            'fields': ('privacy_policy', 'terms_of_service'),
            'classes': ('collapse',)
        }),
        ('Bank Transfer Details', {
            'fields': ('bank_name', 'bank_account_name', 'bank_account_number', 'bank_iban', 'bank_swift_bic'),
            'description': 'These details are shown in order confirmation emails when the customer selects bank transfer.',
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
