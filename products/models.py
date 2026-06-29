from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    STRAIN_TYPE_CHOICES = [
        ('Sativa', 'Sativa'),
        ('Indica', 'Indica'),
        ('Hybrid', 'Hybrid'),
        ('Other', 'Other'),
    ]

    RATIO_CHOICES = [
        ('high_cbd', 'High CBD (20:1)'),
        ('balanced', 'Balanced (1:1)'),
        ('high_thc', 'High THC (1:20)'),
    ]

    CONSUMPTION_METHODS = [
        ('flower', 'Flower'),
        ('oil', 'Oils & Tinctures'),
        ('edible', 'Edibles'),
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Filters/Tags
    strain_type = models.CharField(
        max_length=10,
        choices=STRAIN_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Dominant strain type for this category"
    )

    preferred_ratio = models.CharField(
        max_length=20,
        choices=RATIO_CHOICES,
        blank=True,
        null=True,
        help_text="Suggested cannabinoid ratio for products in this category"
    )

    recommended_methods = models.JSONField(
        blank=True,
        null=True,
        help_text="Suggested consumption methods (e.g., ['flower', 'oil'])"
    )

    # Medical Display Info
    primary_benefits = models.TextField(
        blank=True,
        help_text="Key therapeutic benefits shown in medical section"
    )
    dosage_advice = models.TextField(
        blank=True,
        help_text="Recommended dosing guidance for category"
    )
    effects_timeline = models.TextField(
        blank=True,
        help_text="Expected onset and duration of effects"
    )
    storage_advice = models.TextField(
        blank=True,
        help_text="Proper storage instructions"
    )

    # Misc
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    icon = models.CharField(
        max_length=50,
        blank=True,
        default='fas fa-cannabis',
        help_text="Font Awesome icon class"
    )
    is_medical = models.BooleanField(default=False)
    is_recreational = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    def get_strain_color(self):
        if self.strain_type == 'Sativa':
            return 'bg-green-100 text-green-800'
        elif self.strain_type == 'Indica':
            return 'bg-purple-100 text-purple-800'
        else:
            return 'bg-blue-100 text-blue-800'


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(help_text="Rich text description of the product")
    composition = models.TextField(help_text="Key elements or ingredients")
    usage_instructions = models.TextField(help_text="How to use this product")
    creation_method = models.TextField(help_text="How it is produced or formulated")
    benefits = models.TextField(help_text="Health benefits")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords")
    
    # Additional fields
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    stock_quantity = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    strain_type = models.CharField(
        max_length=10,
        choices=Category.STRAIN_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    preferred_ratio = models.CharField(
        max_length=20,
        choices=Category.RATIO_CHOICES,
        blank=True,
        null=True,
    )
    recommended_methods = models.JSONField(
        blank=True,
        null=True,
        help_text="e.g., ['flower', 'oil']"
    )
    # Rating fields
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=0.00,
        help_text="Automatically calculated average rating (0-5)"
    )
    rating_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of ratings received"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['featured', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def update_rating(self, new_rating):
        """Update the average rating when a new rating is received"""
        total_ratings = self.average_rating * self.rating_count
        self.rating_count += 1
        self.average_rating = (total_ratings + new_rating) / self.rating_count
        self.save()

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
