from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category


def product_list(request):
    """Display all products with advanced filtering"""
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(composition__icontains=query) |
            Q(benefits__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Filters
    filters = {
        'category': request.GET.get('category'),
        'strain_type': request.GET.getlist('strain'),
        'ratio': request.GET.get('ratio'),
        'min_price': request.GET.get('min_price'),
        'max_price': request.GET.get('max_price'),
        'method': request.GET.getlist('method'),
        'in_stock': request.GET.get('in_stock'),
    }
    
    # Apply filters
    if filters['category']:
        products = products.filter(category__slug=filters['category'])
    
    if filters['strain_type']:
        products = products.filter(strain_type__in=filters['strain_type'])
    
    if filters['ratio']:
        products = products.filter(preferred_ratio=filters['ratio'])
    
    if filters['min_price']:
        products = products.filter(price__gte=filters['min_price'])
    
    if filters['max_price']:
        products = products.filter(price__lte=filters['max_price'])
    
    if filters['method']:
        products = products.filter(recommended_methods__overlap=filters['method'])

    if filters['in_stock']:
        products = products.filter(stock_quantity__gt=0)

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = None
    if filters['category']:
        try:
            category = Category.objects.get(slug=filters['category'])
        except Category.DoesNotExist:
            pass

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category': category,
        'query': query,
        'filters': filters,
        'strain_choices': Category.STRAIN_TYPE_CHOICES,
        'ratio_choices': Category.RATIO_CHOICES,
        'method_choices': Category.CONSUMPTION_METHODS,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    """Display product detail page with all information"""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True
    )
    
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def category_detail(request, slug):
    """Display products in a specific category with applied filters"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Strain type filter
    strain_type = request.GET.get('strain_type')
    if strain_type:
        products = products.filter(strain_type=strain_type)

    # Ratio filter
    ratio = request.GET.get('ratio')
    if ratio:
        products = products.filter(preferred_ratio=ratio)

    # Consumption method filter
    methods = request.GET.getlist('method')
    if methods:
        products = products.filter(recommended_methods__overlap=methods)

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'min_price': min_price,
        'max_price': max_price,
        'active_filters': {
            'strain_type': strain_type,
            'ratio': ratio,
            'methods': methods,
        },
        'strain_choices': Category.STRAIN_TYPE_CHOICES,
        'ratio_choices': Category.RATIO_CHOICES,
        'method_choices': Category.CONSUMPTION_METHODS,
        'request': request,  # Make sure request is in context
    }
    return render(request, 'products/category_detail.html', context)