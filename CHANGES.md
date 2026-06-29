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

---

## Phase 5 — Local PostgreSQL Setup & Cloudinary Image Storage

**Date:** 2026-06-29

### Files Changed

| File | Action |
|------|--------|
| `requirements.txt` | Added `cloudinary`, `django-cloudinary-storage` |
| `medicalstore/settings.py` | Added Cloudinary apps + config block |
| `.env.example` | Updated DATABASE_URL comment; added Cloudinary keys |
| `render.yaml` | Added three Cloudinary env vars (`sync: false`) |
| `CHANGES.md` | This document |

---

### Part 1 — Local PostgreSQL Setup

#### Database configuration (already correct — confirmed working)

`settings.py` already uses `dj_database_url.config()` with a SQLite fallback:

```python
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
```

- **No `DATABASE_URL` in `.env`** → SQLite is used automatically (zero config for local dev).
- **`DATABASE_URL` set** → PostgreSQL (or any other DB) is used instead.

#### Setting up a local PostgreSQL database (optional)

If you want to develop against PostgreSQL locally (to match production):

```bash
# 1. Install PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# 2. Create the database and user
sudo -u postgres psql <<'SQL'
CREATE DATABASE medicalstore_dev;
CREATE USER medicalstore_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE medicalstore_dev TO medicalstore_user;
SQL

# 3. Set DATABASE_URL in your .env
# DATABASE_URL=postgresql://medicalstore_user:yourpassword@localhost:5432/medicalstore_dev

# 4. Run migrations against the new database
python manage.py migrate
```

To go back to SQLite, comment out or remove `DATABASE_URL` from `.env`.

---

### Part 2 — Cloudinary for Image Storage

#### How the conditional logic works

Cloudinary is **opt-in**: the app checks whether all three keys are non-empty at startup. This means:

| Environment | Keys set? | Storage used |
|-------------|-----------|--------------|
| Local dev (default) | No | Django's default local filesystem (`MEDIA_ROOT`) |
| Local dev (with Cloudinary) | Yes | Cloudinary |
| Render (production) | Yes (from dashboard) | Cloudinary |

The check in `settings.py`:

```python
if all([
    config('CLOUDINARY_CLOUD_NAME', default=''),
    config('CLOUDINARY_API_KEY', default=''),
    config('CLOUDINARY_API_SECRET', default=''),
]):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

If any key is missing or blank, `DEFAULT_FILE_STORAGE` is never set and Django falls back to its built-in local filesystem storage. No code change is needed in models — existing `ImageField` definitions work transparently with either backend.

#### INSTALLED_APPS order (required by django-cloudinary-storage)

```python
INSTALLED_APPS = [
    ...
    'cloudinary_storage',        # ← must be BEFORE django.contrib.staticfiles
    'django.contrib.staticfiles',
    'cloudinary',                # ← after django.contrib.staticfiles
    ...
]
```

#### Local development without Cloudinary

Just leave the three keys out of `.env` (or blank). Product images are stored in `media/products/` as before. No Cloudinary account needed.

#### Local development with Cloudinary

Add your keys to `.env`:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Uploaded images will go to Cloudinary automatically.

---

### Render Deployment Checklist

Set the following in the Render dashboard → your service → **Environment** (all marked `sync: false` — never committed):

| Variable | Where to get it |
|----------|----------------|
| `SMTP_PASSWORD` | Your email provider |
| `CLOUDINARY_CLOUD_NAME` | cloudinary.com → Dashboard |
| `CLOUDINARY_API_KEY` | cloudinary.com → Dashboard |
| `CLOUDINARY_API_SECRET` | cloudinary.com → Dashboard |

All other variables are declared in `render.yaml` and set automatically.

---

### Complete Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Django secret key (50+ random chars) |
| `DEBUG` | No | `False` | Set to `True` for local dev only |
| `ALLOWED_HOSTS` | **Yes** | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | No | `''` | Comma-separated trusted origins (include production URL) |
| `DATABASE_URL` | No | SQLite fallback | PostgreSQL connection string; omit for SQLite |
| `SMTP_EMAIL` | No | `''` | SMTP sender address |
| `SMTP_PASSWORD` | No | `''` | SMTP password (**never commit**) |
| `SMTP_HOST` | No | `smtp.hostinger.com` | SMTP server hostname |
| `SMTP_PORT` | No | `465` | SMTP port |
| `ADMIN_EMAIL` | No | `admin@example.com` | Receives order notification emails |
| `DEFAULT_FROM_EMAIL` | No | `info@example.com` | Email From: header |
| `CLOUDINARY_CLOUD_NAME` | No | `''` | Cloudinary cloud name; leave blank for local file storage |
| `CLOUDINARY_API_KEY` | No | `''` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | No | `''` | Cloudinary API secret (**never commit**) |

---

## Phase 6 — Complete Authentication Flow

**Date:** 2026-06-29

### Audit Findings

| Template | Before | After |
|---|---|---|
| `registration/login.html` | Existed, styled | Unchanged |
| `registration/register.html` | Existed, styled | Unchanged |
| `accounts/profile.html` | Existed, styled | Unchanged |
| `registration/password_reset_form.html` | Missing (Django unstyled default) | **Created** |
| `registration/password_reset_done.html` | Missing (Django unstyled default) | **Created** |
| `registration/password_reset_confirm.html` | Missing (Django unstyled default) | **Created** |
| `registration/password_reset_complete.html` | Missing (Django unstyled default) | **Created** |
| `registration/password_change_form.html` | Missing (Django unstyled default) | **Created** |
| `registration/password_change_done.html` | Missing (Django unstyled default) | **Created** |
| `registration/logged_out.html` | Not needed | Not created (custom `logout_view` redirects to home) |

### Bug Fixed

**File:** `accounts/forms.py:20`

`focus:ring-medical-blue` was not a defined Tailwind color — focus rings on all register form
inputs were invisible. Fixed to `focus:ring-cannabis-green`.

### Files Changed

| File | Action |
|---|---|
| `accounts/forms.py` | Fixed CSS class (`medical-blue` → `cannabis-green`) |
| `templates/registration/password_reset_form.html` | **Created** |
| `templates/registration/password_reset_done.html` | **Created** |
| `templates/registration/password_reset_confirm.html` | **Created** |
| `templates/registration/password_reset_complete.html` | **Created** |
| `templates/registration/password_change_form.html` | **Created** |
| `templates/registration/password_change_done.html` | **Created** |

### URL Wiring — Verified

All Django auth URL names resolve correctly under `i18n_patterns`:

| URL name | Path | View |
|---|---|---|
| `login` | `/accounts/login/` | Django built-in `LoginView` |
| `logout` | `/accounts/logout/` | Custom `logout_view` (GET-safe, redirects to home) |
| `accounts:logout` | `/accounts/logout/` | Same custom view (app-namespaced alias) |
| `password_reset` | `/accounts/password_reset/` | Django `PasswordResetView` |
| `password_reset_done` | `/accounts/password_reset/done/` | Django `PasswordResetDoneView` |
| `password_reset_confirm` | `/accounts/reset/<uidb64>/<token>/` | Django `PasswordResetConfirmView` |
| `password_reset_complete` | `/accounts/reset/done/` | Django `PasswordResetCompleteView` |
| `password_change` | `/accounts/password_change/` | Django `PasswordChangeView` |
| `password_change_done` | `/accounts/password_change/done/` | Django `PasswordChangeDoneView` |
| `accounts:register` | `/accounts/register/` | Custom `register` view |
| `accounts:profile` | `/accounts/profile/` | Custom `profile` view (`@login_required`) |

**Logout routing note:** `accounts.urls` is included before `django.contrib.auth.urls` in
`urls.py`. Both patterns match `/accounts/logout/`, but Django's URL dispatcher reaches the
custom `logout_view` first. `{% url 'logout' %}` and `{% url 'accounts:logout' %}` both
generate the same path and invoke the same view.

### Auth Flow Verification (all tested)

| Flow | Result |
|---|---|
| Register → POST `/accounts/register/` | 302 → `/` |
| Login with wrong password | 200 (form redisplayed with error) |
| Login with correct password | 302 → `/` |
| Logout GET `/accounts/logout/` | 302 → `/` |
| Password reset form GET | 200 |
| Password reset form POST | 302 → `/accounts/password_reset/done/` |
| Password change (unauthenticated) | 302 → `/accounts/login/?next=/accounts/password_change/` |
| Password change form GET (auth) | 200 |
| Password change form POST (auth) | 302 → `/accounts/password_change/done/` |
| Profile (unauthenticated) | 302 → `/accounts/login/?next=/accounts/profile/` |
| Profile (authenticated) | 200 |

**Password reset email in local dev:** The form correctly redirects to the done page. The
actual SMTP send fails locally (no live connection) — this is expected. In production,
`SMTP_PASSWORD` must be set in the Render dashboard for emails to send.

### How to Test the Full Auth Flow Locally

```bash
# Start the dev server
python manage.py runserver

# 1. Register
#    Visit: http://localhost:8000/accounts/register/
#    Fill in all fields and submit → should land on home page, logged in

# 2. Logout
#    Click Logout in the nav → should redirect to home, no longer logged in

# 3. Login wrong password
#    Visit: http://localhost:8000/accounts/login/
#    Enter wrong password → error message shown inline

# 4. Login correct
#    Enter correct credentials → redirects to home

# 5. Password reset (requires SMTP configured)
#    Visit: http://localhost:8000/accounts/password_reset/
#    Enter your email → redirects to done page (email sent if SMTP works)
#    Click link in email → /accounts/reset/<uid>/<token>/
#    Enter new password → redirects to complete page

# 6. Change password (while logged in)
#    Visit: http://localhost:8000/accounts/password_change/
#    Enter current + new password → redirects to done page

# 7. Profile
#    Visit: http://localhost:8000/accounts/profile/
#    (Redirects to login if not authenticated)
```

---

## Phase 7 — Custom Django Admin

**Date:** 2026-06-29

### Files Changed

| File | Action |
|---|---|
| `products/models.py` | Added `Category.image` field |
| `products/migrations/0010_add_category_image.py` | **Created** (auto) |
| `products/widgets.py` | **Created** — CloudinaryImageWidget |
| `products/admin.py` | Full rewrite — CategoryAdmin + ProductAdmin + StockStatusFilter |
| `orders/admin.py` | Full rewrite — OrderAdmin + OrderItemInline + CSV export |
| `accounts/admin.py` | Full rewrite — CustomUserAdmin (extends BaseUserAdmin) |
| `pages/admin.py` | Full rewrite — enhanced SiteSettingsAdmin |
| `medicalstore/admin_site.py` | **Created** — MedicalStoreAdminSite with stats dashboard |
| `medicalstore/urls.py` | Updated to use `admin_site.urls` |
| `medicalstore/settings.py` | Replaced `STATICFILES_STORAGE`+`DEFAULT_FILE_STORAGE` with `STORAGES` dict (Django 5.0 requirement) |
| `templates/admin/base_site.html` | **Created** — cannabis-green branding |
| `templates/admin/index.html` | **Created** — full stats dashboard |

### Critical Fix: Django 5.0 Storage Config

`DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` were removed in Django 5.0.
Both must now be set via the `STORAGES` dict:

```python
STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage'  # or FileSystemStorage
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # or StaticFilesStorage
    },
}
```

Setting `DEFAULT_FILE_STORAGE` in Django 5.x is silently ignored — images would
upload to local filesystem even when Cloudinary keys are present.

### Cloudinary Widget (`products/widgets.py`)

`CloudinaryImageWidget(ClearableFileInput)` shows:
- 150×150 thumbnail of current image
- Green "On Cloudinary" badge when URL contains `cloudinary.com`
- Orange "Stored locally" badge otherwise
- Clickable URL link
- Standard file input for new uploads

Used in both `CategoryAdmin` and `ProductAdmin` via `formfield_overrides = {ImageField: {'widget': CloudinaryImageWidget}}`.

### Custom AdminSite (`medicalstore/admin_site.py`)

`MedicalStoreAdminSite(AdminSite)` overrides `index()` to inject:

| Context variable | Content |
|---|---|
| `stat_total_products` / `stat_active_products` / `stat_inactive_products` | Product counts |
| `stat_total_categories` | Category count |
| `stat_total_orders` / `stat_pending_orders` | Order counts |
| `stat_revenue` | Sum of delivered order totals |
| `stat_low_stock` / `stat_out_of_stock` | Stock level counts |
| `stat_registered_users` | User count |
| `recent_orders` | Last 10 orders |
| `low_stock_products` | 10 products with lowest stock |

All models registered with `@admin.register(Model, site=admin_site)` (not `@admin.register(Model)`) so they appear in the custom site only.

### Admin Features Summary

**Products:**
- `StockStatusFilter` — sidebar filter with Out/Low/In Stock options; dashboard cards link to `?stock_status=out` and `?stock_status=low`
- `stock_badge` — colored pill badge per stock level
- `image_preview` — 50×50 thumbnail with Cloudinary/Local badge
- 4 bulk actions: mark_active, mark_inactive, mark_featured, unmark_featured

**Orders:**
- `order_number` — `ORD-00001` format
- `status_badge` — colored pill per status
- `OrderItemInline` — shows line_total (price × quantity) as readonly
- CSV export action — downloads all selected orders as `.csv`
- Status bulk actions: mark_processing, mark_shipped, mark_delivered, mark_cancelled

**Users:**
- Extends Django's `BaseUserAdmin`
- `order_count` — clickable link to that user's orders
- `Group` registered so group management is available

### How to Test Cloudinary Upload from Admin

1. Put real Cloudinary credentials in `.env` (get from cloudinary.com → Dashboard)
2. Start server: `python manage.py runserver`
3. Go to `/admin/products/product/add/`
4. Upload an image and save
5. Verify in shell:
```bash
python manage.py shell -c "
from products.models import Product
p = Product.objects.last()
print(p.image.url)
# Must contain: cloudinary.com
"
```
6. The stored URL will be `https://res.cloudinary.com/<your-cloud>/image/upload/.../products/<filename>`

### Credentials Needed (all marked sync: false in render.yaml)

| Variable | Where to get it |
|---|---|
| `CLOUDINARY_CLOUD_NAME` | cloudinary.com → Dashboard → Cloud Name |
| `CLOUDINARY_API_KEY` | cloudinary.com → Dashboard → API Key |
| `CLOUDINARY_API_SECRET` | cloudinary.com → Dashboard → API Secret |

---

## Phase 8 — populate_db Management Command

**Date:** 2026-06-29

### Summary

Created idempotent seed commands based on the real data extracted from `db.sqlite3`.
Running `populate_db` twice produces **0 new records** on the second run.

**Counts seeded:**
- 20 categories (15 cannabis + 5 medical/pharmaceutical)
- 17 products (7 cannabis + 10 medical)
- 1 SiteSettings record

### Files Changed

| File | Action |
|---|---|
| `products/management/commands/populate_db.py` | Full rewrite — all real data, idempotent |
| `products/management/commands/clear_db.py` | **Created** — utility to wipe products/categories |
| `render.yaml` | `buildCommand` updated to run `populate_db` after `migrate` |

### populate_db (`python manage.py populate_db`)

- Uses `update_or_create(slug=slug, defaults={...})` for both categories and products
- Sets all translated fields (`name_en`, `name_fr`, `description_en`, `description_fr`, etc.)
- Skips image fields — images must be uploaded manually via `/admin/` to Cloudinary
- Truncates `meta_description` fields to 160 chars (PostgreSQL `character varying(160)` limit)
- Prints per-record status: `Created: <name>` or `Skipped existing: <name>`
- Final line always: `Database populated successfully.`

**Running locally:**
```bash
python manage.py populate_db
```

**Running on a fresh deploy:**
`render.yaml buildCommand` now runs it automatically after every `migrate`:
```
... && python manage.py migrate && python manage.py populate_db
```
Since it uses `update_or_create`, re-running on deploy only updates changed records and
skips everything that already exists — no duplicates possible.

### clear_db (`python manage.py clear_db`)

Utility command for local development. Deletes all Products, Categories, and SiteSettings.
Does **not** delete users or orders.

```bash
python manage.py clear_db
# → "This will delete 17 product(s), 20 category/ies, and 1 SiteSettings record(s)."
# → "Type YES to confirm: "
```

Useful workflow for a clean re-seed:
```bash
python manage.py clear_db   # type YES
python manage.py populate_db
```

### Category slugs seeded

| Slug | Name (EN) | Type |
|---|---|---|
| `thc-flower` | THC Flower | Cannabis |
| `cbd-flower` | CBD Flower | Cannabis |
| `backpack-boyz` | Backpack Boyz | Cannabis brand |
| `doja-exclusive` | Doja Exclusive | Cannabis brand |
| `jungle-boys` | Jungle Boys | Cannabis brand |
| `the-ten-co` | The TEN Co | Cannabis brand |
| `wizard-trees` | Wizard Trees | Cannabis brand |
| `cookies-strains` | Cookies Strains | Cannabis brand |
| `hash` | Hash | Cannabis concentrate |
| `thc-diamond` | THC Diamonds | Cannabis concentrate |
| `thc-candy` | THC Candy | Cannabis edible |
| `thc-oil` | THC Oil | Cannabis oil |
| `cbd-oil` | CBD Oil | CBD |
| `cannabis-tincture` | Cannabis Tincture | CBD |
| `magic-mushrooms` | Magic Mushrooms | Other |
| `pain-relief` | Pain Relief | Medical |
| `cardiovascular-health` | Cardiovascular Health | Medical |
| `digestive-health` | Digestive Health | Medical |
| `immune-support` | Immune Support | Medical |
| `respiratory-care` | Respiratory Care | Medical |
