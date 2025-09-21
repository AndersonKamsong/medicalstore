from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Site-wide settings that can be configured from admin"""
    site_name = models.CharField(_('Site Name'), max_length=100, default='Green Houses CBD')
    tagline = models.CharField(_('Tagline'), max_length=200, default='Premium Natural Medical Products')
    
    # Contact Information
    email = models.EmailField(_('Email'), default='info@greenhousescbd.com')
    phone = models.CharField(_('Phone'), max_length=20, default='+33 1 23 45 67 89')
    address = models.TextField(_('Address'), default='Paris, France')
    
    # Social Media
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    
    # Business Information
    business_hours = models.TextField(_('Business Hours'), default='Mon-Fri: 9:00-18:00\nSat: 10:00-16:00\nSun: Closed')
    about_text = models.TextField(_('About Text'), default='We specialize in premium natural medical products derived from organic sources.')
    
    # Legal
    privacy_policy = models.TextField(_('Privacy Policy'), blank=True)
    terms_of_service = models.TextField(_('Terms of Service'), blank=True)
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Only one SiteSettings instance is allowed')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
