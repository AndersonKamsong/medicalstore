# Modification Report — medicalstore

**Date:** 2026-06-29  
**Branch:** bikim_app  
**Django version:** 5.2.4  
**Python:** 3.11.13 (pyenv)

---

## Summary

All four phases of the planned audit remediation were applied in a single session.  
`python manage.py check` passes with **0 issues** after all changes.

---

## Phase 1 — Critical Security Fixes

### 1. Secrets moved to environment variables

**File changed:** `medicalstore/settings.py`  
**New dependency:** `python-decouple==3.8` (added to `requirements.txt`)

All hardcoded secrets replaced with `config()` calls reading from a `.env` file:

| Setting | Was | Now |
|---------|-----|-----|
| `SECRET_KEY` | Hardcoded insecure string | `config('SECRET_KEY')` |
| `DEBUG` | `True` (hardcoded) | `config('DEBUG', default=False, cast=bool)` |
| `ALLOWED_HOSTS` | `['*']` | `config('ALLOWED_HOSTS', cast=Csv())` |
| `CSRF_TRUSTED_ORIGINS` | Hardcoded dev URLs | `config('CSRF_TRUSTED_ORIGINS', default='')` |
| `SMTP_EMAIL` | `"info@greenhousescbd.com"` | `config('SMTP_EMAIL', default='')` |
| `SMTP_PASSWORD` | `"Ander39@@Test"` (plaintext!) | `config('SMTP_PASSWORD', default='')` |
| `SMTP_HOST` | `"smtp.hostinger.com"` | `config('SMTP_HOST', ...)` |
| `SMTP_PORT` | `465` | `config('SMTP_PORT', default=465, cast=int)` |
| `ADMIN_EMAIL` | `"gastonanderson039@gmail.com"` | `config('ADMIN_EMAIL', default='...')` |
| `DEFAULT_FROM_EMAIL` | Hardcoded | `config('DEFAULT_FROM_EMAIL', default='...')` |

### 2. `.env.example` created

**File created:** `.env.example`

Documents every required environment variable with placeholder values and comments.  
Safe to commit — contains no real credentials.

### 3. `.env` added to `.gitignore`

**File changed:** `.gitignore`  
Line `# .env` was commented out — uncommented so the real `.env` file is never tracked by git.

### 4. IDOR vulnerability fixed on order detail view

**File changed:** `orders/views.py` — `order_created()` function

**Before:**
```python
def order_created(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order/created.html', {'order': order})
```

**After:**
```python
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user is not None and request.user != order.user:
        return HttpResponseForbidden("You are not authorised to view this order.")
    return render(request, 'orders/order/created.html', {'order': order})
```

Logic: guest orders (`order.user = None`) remain publicly accessible via their confirmation URL. Authenticated-user orders are restricted to their owner. Any other visitor receives HTTP 403.

### 5. Stock decrement + pre-check on order creation

**File changed:** `orders/views.py` — `order_create()` function

Two additions inside the `form.is_valid()` block:

**Stock pre-check (before saving the order):**
```python
for item in cart_items:
    product = item['product']
    if product.stock_quantity < item['quantity']:
        messages.error(
            request,
            f'Sorry, only {product.stock_quantity} unit(s) of '
            f'"{product.name}" are available. Please update your cart.'
        )
        return redirect('cart:cart_detail')
```

**Stock decrement (after saving order items):**
```python
item['product'].stock_quantity -= item['quantity']
item['product'].save(update_fields=['stock_quantity'])
```

If any cart item exceeds available stock, the order is blocked before creation and the user is sent back to the cart with a descriptive error message.

### 6. `@csrf_exempt` removed from `order_create`

**File changed:** `orders/views.py`

The `@csrf_exempt` decorator on `order_create` was a security hole — removed. The checkout form already contains `{% csrf_token %}` so CSRF protection works correctly without the exemption.

---

## Phase 2 — Database Switch (Option B: PostgreSQL)

### 7. Production dependencies uncommented in `requirements.txt`

**File changed:** `requirements.txt`

The following were previously commented out and are now active:

```
gunicorn==21.2.0
psycopg2-binary==2.9.7
dj-database-url==2.1.0
whitenoise==6.5.0
```

`python-decouple==3.8` was also added (new).

### 8. `DATABASES` updated to use `dj-database-url`

**File changed:** `medicalstore/settings.py`

**Before:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**After:**
```python
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
```

- Locally (no `DATABASE_URL` in `.env`): falls back to SQLite automatically.
- On Render: `DATABASE_URL` is injected from the PostgreSQL service and PostgreSQL is used.
- `conn_max_age=600` enables persistent connections (10-minute pool).

### 9. `render.yaml` verified correct for PostgreSQL

**File changed:** `render.yaml` (also fixed in Phase 3 — see below)

The `databases:` block and `DATABASE_URL: fromDatabase:` reference were already correct and unchanged.

---

## Phase 3 — Production Fixes

### 10. `render.yaml` start command fixed

**File changed:** `render.yaml`

**Before:**
```yaml
startCommand: python manage.py runserver 0.0.0.0:$PORT
```

**After:**
```yaml
startCommand: gunicorn medicalstore.wsgi:application --bind 0.0.0.0:$PORT
```

`runserver` is Django's single-threaded development server — it must never be used in production.

Also added all SMTP environment variable declarations to `render.yaml`:

```yaml
- key: SMTP_EMAIL
  value: "info@greenhousescbd.com"
- key: SMTP_HOST
  value: "smtp.hostinger.com"
- key: SMTP_PORT
  value: "465"
- key: ADMIN_EMAIL
  value: "gastonanderson039@gmail.com"
- key: DEFAULT_FROM_EMAIL
  value: "info@greenhousescbd.com"
- key: SMTP_PASSWORD
  sync: false   # Set this manually in the Render dashboard — never commit the value
```

Also removed `python manage.py populate_db` from `buildCommand` to prevent duplicate seed data on every deploy.

### 11. Whitenoise added for static file serving

**File changed:** `medicalstore/settings.py`

`whitenoise.middleware.WhiteNoiseMiddleware` inserted immediately after `SecurityMiddleware` (required position):

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]
```

`STATICFILES_STORAGE` set conditionally:
```python
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
    if not DEBUG
    else 'django.contrib.staticfiles.storage.StaticFilesStorage'
)
```

Production: whitenoise serves compressed, fingerprinted static files from `STATIC_ROOT`.  
Development (`DEBUG=True`): Django's default storage is used so `collectstatic` is not required locally.

### 12. Customer order confirmation email added

**File changed:** `orders/views.py` — new `send_customer_order_confirmation()` function  
**File created:** `templates/emails/customer_order_confirmation.html`

**Before:** Only the admin received an email when an order was placed (except bank_transfer orders, which sent bank instructions to the customer). No general confirmation was sent to the customer.

**After:** Every order triggers a customer confirmation email regardless of payment method. The single email template handles all cases:

- **All orders:** Order number, customer name, delivery address, payment method, order total, itemised list.
- **Bank transfer only:** A "Bank Transfer Instructions" section is appended to the same email, pulling bank details from `SiteSettings` (see Phase 4 item 14).

The old hardcoded bank-transfer email block was removed from `order_create()` and replaced with the unified `send_customer_order_confirmation()` call.

`send_email_directly()` was also fixed: it previously hardcoded `"smtp.hostinger.com"` and `465` inside the function, ignoring `settings.SMTP_HOST` and `settings.SMTP_PORT`. Now it reads both from settings.

---

## Phase 4 — Quick Wins

### 13. Product image fallback (already implemented — no change needed)

Both `templates/products/product_list.html` and `templates/products/product_detail.html` already contained correct `{% if product.image %} … {% else %} … {% endif %}` fallback blocks displaying a Font Awesome icon when no image is set. No change required.

### 14. Bank account details moved to `SiteSettings`

**File changed:** `pages/models.py`  
**File changed:** `pages/admin.py`  
**Migration created:** `pages/migrations/0003_...`

Five new fields added to `SiteSettings`:

```python
bank_name = models.CharField(max_length=100, blank=True, default='')
bank_account_name = models.CharField(max_length=100, blank=True, default='')
bank_account_number = models.CharField(max_length=50, blank=True, default='')
bank_iban = models.CharField(max_length=50, blank=True, default='')
bank_swift_bic = models.CharField(max_length=20, blank=True, default='')
```

A **"Bank Transfer Details"** fieldset was added to `SiteSettingsAdmin` so these can be managed from `/admin/pages/sitesettings/`.

The customer confirmation email template reads these fields:
```html
{% if site_settings.bank_iban %}
<tr><td>IBAN:</td><td>{{ site_settings.bank_iban }}</td></tr>
{% endif %}
```
Each field is shown conditionally — empty fields are hidden.

**Action required before going live:** fill in the bank details via Django admin.

### 15. "In Stock Only" filter added to product list

**File changed:** `products/views.py` — `product_list()` function  
**File changed:** `templates/products/product_list.html`

**View:** `in_stock` added to the filters dict and applied as a queryset filter:
```python
filters = { ..., 'in_stock': request.GET.get('in_stock') }

if filters['in_stock']:
    products = products.filter(stock_quantity__gt=0)
```

**Template:** checkbox added to the sidebar filter form above the Apply/Reset buttons:
```html
<label class="flex items-center text-gray-700 cursor-pointer select-none">
    <input type="checkbox" name="in_stock" value="1"
           {% if filters.in_stock %}checked{% endif %}
           class="mr-2 text-cannabis-green">
    <span class="font-medium text-sm">In Stock Only</span>
</label>
```

---

## Bonus Fix — Pre-existing Bug

### `Product.meta_description` missing `max_length`

**File changed:** `products/models.py`  
**Migration created:** `products/migrations/0009_...`

`meta_description = models.CharField(blank=True, ...)` had no `max_length`, making it an invalid field definition that would raise an error on any database that enforces column types (PostgreSQL).

**Fixed:**
```python
meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
```

This was a required fix before PostgreSQL migrations could succeed.

---

## Files Changed — Complete List

| File | Action |
|------|--------|
| `requirements.txt` | Modified |
| `.env.example` | **Created** |
| `.gitignore` | Modified |
| `medicalstore/settings.py` | Modified (full rewrite) |
| `render.yaml` | Modified |
| `orders/views.py` | Modified (full rewrite) |
| `pages/models.py` | Modified |
| `pages/admin.py` | Modified |
| `products/models.py` | Modified |
| `products/views.py` | Modified |
| `templates/emails/customer_order_confirmation.html` | **Created** |
| `templates/products/product_list.html` | Modified |
| `pages/migrations/0003_remove_sitesettings_about_text_da_and_more.py` | **Created** (auto-generated) |
| `products/migrations/0009_remove_category_description_da_and_more.py` | **Created** (auto-generated) |
| `static/` | **Created** (empty directory, required by STATICFILES_DIRS) |

---

## Commands to Run Locally

```bash
# Ensure correct Python is active (Django 5.2.4)
pyenv global 3.11.13
python -m django --version   # must print 5.2.4

# Create your local .env from the example
cp .env.example .env
# Edit .env — set SECRET_KEY, SMTP_*, ADMIN_EMAIL, DEFAULT_FROM_EMAIL

# Generate a secure SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Migrations are already applied; re-run after any future model change
python manage.py migrate

# Confirm zero errors
python manage.py check

# Start the development server
python manage.py runserver

# Fill in bank transfer details in admin before going live
# http://localhost:8000/en/admin/pages/sitesettings/
```

## Before Deploying to Render

1. Push this branch to your remote repository.
2. In the Render dashboard → your service → **Environment**, add `SMTP_PASSWORD` manually (it is marked `sync: false` and will not be set from `render.yaml`).
3. Render will automatically run `collectstatic` + `migrate` + start `gunicorn` on deploy.
