# Medicalstore Django Project — Full Audit Report

---

## 1. Project Overview

**Framework:** Django 5.2.4
**Database:** SQLite (`db.sqlite3`)
**Language support:** English + French (via `django-modeltranslation`)
**Frontend:** Tailwind CSS (CDN), Alpine.js, Font Awesome
**Deployment target:** Render.com (render.yaml present)

---

## 2. Apps and Their Responsibilities

| App | Purpose |
|-----|---------|
| `products` | Product catalog, categories, filtering, search, pagination |
| `cart` | Session-based shopping cart (not DB-backed) |
| `orders` | Checkout, order creation, order history, email notifications |
| `accounts` | User registration, login, logout, profile |
| `pages` | Static informational pages (home, about, FAQ, legal, privacy, etc.) + SiteSettings model |
| `medicalstore` | Project-level config (settings, root URLs, wsgi/asgi) |

Third-party app: `modeltranslation` for bi-lingual model fields.

---

## 3. All Models and Their Fields

### `products.Category`

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Translated (EN/FR) |
| `slug` | SlugField | Unique |
| `description` | TextField | Translated |
| `meta_title` | CharField | SEO |
| `meta_description` | TextField | SEO |
| `strain_type` | CharField | choices: Sativa, Indica, Hybrid, Other |
| `ratio` | CharField | CBD:THC ratios |
| `methods` | CharField | Consumption methods |
| `icon` | CharField | Icon class name |
| `image` | ImageField | Optional |
| `medical_condition` | TextField | Medical info |
| `medical_benefits` | TextField | Translated |
| `dosage_info` | TextField | Translated |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |

### `products.Product`

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(200) | Translated |
| `slug` | SlugField | Unique |
| `category` | FK → Category | on_delete=CASCADE |
| `price` | DecimalField(10,2) | |
| `description` | TextField | Translated |
| `composition` | TextField | Translated |
| `usage_instructions` | TextField | Translated |
| `creation_method` | TextField | Translated |
| `benefits` | TextField | Translated |
| `image` | ImageField | upload_to='products/' |
| `meta_title` | CharField | SEO |
| `meta_description` | TextField | SEO |
| `stock_quantity` | IntegerField | Default 0 |
| `is_active` | BooleanField | Default True |
| `featured` | BooleanField | Default False |
| `strain_type` | CharField | choices |
| `ratio` | CharField | CBD:THC |
| `methods` | CharField | Consumption method |
| `rating` | DecimalField | Not wired to UI |
| `num_reviews` | IntegerField | Not wired to UI |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |

### `orders.Order`

| Field | Type | Notes |
|-------|------|-------|
| `user` | FK → User | null/blank=True |
| `first_name` | CharField(50) | |
| `last_name` | CharField(50) | |
| `email` | EmailField | |
| `address` | CharField(250) | |
| `postal_code` | CharField(20) | |
| `city` | CharField(100) | |
| `country` | CharField(100) | Default 'France' |
| `phone` | CharField(20) | |
| `payment_method` | CharField | choices |
| `status` | CharField | choices: pending/confirmed/shipped/delivered/cancelled |
| `total_amount` | DecimalField(10,2) | |
| `created` | DateTimeField | Auto |
| `updated` | DateTimeField | Auto |

### `orders.OrderItem`

| Field | Type | Notes |
|-------|------|-------|
| `order` | FK → Order | on_delete=CASCADE |
| `product` | FK → Product | on_delete=CASCADE |
| `price` | DecimalField(10,2) | Snapshot at purchase |
| `quantity` | PositiveIntegerField | |

### `pages.SiteSettings`

| Field | Type | Notes |
|-------|------|-------|
| `site_name` | CharField | |
| `tagline` | CharField | |
| `email` | EmailField | |
| `phone` | CharField | |
| `address` | TextField | |
| `facebook/instagram/twitter/youtube` | URLField | Social links |
| `business_hours` | TextField | |
| `about_text` | TextField | |
| `legal_text` | TextField | |
| `privacy_text` | TextField | |
| Singleton | override `save()` | Only 1 row allowed |

### `accounts` App

No custom models. Uses Django's built-in `User` model directly.

---

## 4. All Routes / URLs

All routes are wrapped in `i18n_patterns` (language prefix, e.g. `/en/`, `/fr/`).

### Root (`medicalstore/urls.py`)

| Pattern | Name | View |
|---------|------|------|
| `/admin/` | — | Django admin |
| `/` | includes pages.urls | |
| `/products/` | includes products.urls | |
| `/cart/` | includes cart.urls | |
| `/orders/` | includes orders.urls | |
| `/accounts/` | includes accounts.urls | |

### Pages (`pages/urls.py`)

| Pattern | Name |
|---------|------|
| `` (empty) | `home` |
| `about/` | `about` |
| `contact/` | `contact` |
| `faq/` | `faq` |
| `legal/` | `legal` |
| `privacy/` | `privacy` |
| `services/` | `services` |
| `shipping/` | `shipping` |
| `returns/` | `returns_policy` |
| `crypto-guide/` | `crypto_guide` |
| `change-language/` | `change_language` (POST) |

### Products (`products/urls.py`)

| Pattern | Name |
|---------|------|
| `` | `product_list` |
| `<slug:slug>/` | `product_detail` |
| `category/<slug:slug>/` | `category_detail` |

### Cart (`cart/urls.py`)

| Pattern | Name |
|---------|------|
| `` | `cart_detail` |
| `add/<int:product_id>/` | `cart_add` (POST) |
| `remove/<int:product_id>/` | `cart_remove` (POST) |

### Orders (`orders/urls.py`)

| Pattern | Name |
|---------|------|
| `create/` | `order_create` |
| `created/<int:order_id>/` | `order_created` |
| `history/` | `order_history` (login required) |

### Accounts (`accounts/urls.py`)

| Pattern | Name |
|---------|------|
| `register/` | `register` |
| `profile/` | `profile` (login required) |
| `logout/` | `logout` |
| `accounts/` | Django auth URLs (login, password reset, etc.) |

---

## 5. Current Database Setup

- **Engine:** `django.db.backends.sqlite3`
- **File:** `db.sqlite3` in project root
- **Migrations:** Standard Django migrations
- **Deployment note:** `render.yaml` references a PostgreSQL service (`medicalstore-db`) and runs `migrate` + `populate_db` on build, but `requirements.txt` does **not** include `psycopg2` or `dj-database-url` — this deployment would currently fail.

---

## 6. Bugs, Missing Features, and Security Issues

### Critical Security Issues

| # | Issue | Location |
|---|-------|----------|
| 1 | `SECRET_KEY` hardcoded in plain text | `settings.py:24` |
| 2 | SMTP password hardcoded in plain text | `settings.py:105` |
| 3 | `DEBUG = True` committed to version control | `settings.py:27` |
| 4 | `ALLOWED_HOSTS = ['*']` | `settings.py:31` |
| 5 | `db.sqlite3` tracked in git (contains user/order data) | `.gitignore` / git status |

### High-Priority Bugs

| # | Bug | Impact |
|---|-----|--------|
| 6 | `render.yaml` uses `python manage.py runserver` as production server | Will fail under any real load |
| 7 | `psycopg2-binary`, `gunicorn`, `dj-database-url`, `whitenoise` commented out in `requirements.txt` but needed by `render.yaml` | Production deployment will crash |
| 8 | No stock decrement on order creation — `stock_quantity` is never reduced when an order is placed | Overselling |
| 9 | `send_email_directly()` swallows errors silently — order confirmation emails may fail invisibly | Customers get no confirmation |
| 10 | Cart item prices are stored from session without re-validation against current product price at checkout | Cart total corruption possible |
| 11 | `order_created` view fetches `Order.objects.get(id=order_id)` with no ownership check — any user can view any order by guessing the ID (IDOR vulnerability) | Data leak |

### Medium Issues

| # | Issue |
|---|-------|
| 12 | `rating` and `num_reviews` fields exist on Product but no review/rating system is implemented anywhere |
| 13 | Cart is session-only — cleared on session expiry, not recoverable by logged-in users |
| 14 | No customer-facing order status email — only admin notification is sent |
| 15 | `change_language` view accepts any language code from POST without validation |
| 16 | Bank account details for transfers are hardcoded in the email template — should be in `SiteSettings` |
| 17 | No image placeholder/fallback when `product.image` is empty — broken image tags in templates |
| 18 | `populate_db` management command is called on every deploy in `render.yaml` — could duplicate seed data |

### Low Issues

| # | Issue |
|---|-------|
| 19 | `SESSION_COOKIE_SECURE` and `SESSION_COOKIE_HTTPONLY` are not explicitly set |
| 20 | No `robots.txt` or `sitemap.xml` |
| 21 | Tailwind CSS and Alpine.js loaded from CDN with no integrity hashes (SRI) |
| 22 | Age verification is client-side only (localStorage) — trivially bypassed |
| 23 | No rate limiting on login or registration endpoints |
| 24 | `SiteSettings` singleton uses `pk=1` assumption in `save()` — fragile if DB is reset |

---

## 7. Code Quality Problems

| # | Problem |
|---|---------|
| 1 | `orders/views.py` `send_email_directly()` bypasses Django's email backend entirely — makes testing impossible and duplicates configuration |
| 2 | Views mix business logic (stock check, email sending, price calculation) directly — no service layer or separation of concerns |
| 3 | Cart item prices are stored at add-time but never validated against current product price at checkout |
| 4 | `UserRegistrationForm.save()` re-sets fields already handled by the parent `UserCreationForm.save()` — redundant and fragile |
| 5 | `product_list` view builds filter querystring manually in template context — could use `django-filter` cleanly |
| 6 | Translated fields duplicate column count (`name_en`, `name_fr`) with no fallback strategy if a translation is missing |
| 7 | `render.yaml` `startCommand` uses `runserver` — must be `gunicorn` |
| 8 | Admin `list_editable` on `price` and `stock_quantity` without row-level permission control — any staff user can bulk-edit pricing |

---

## 8. SQLite → MongoDB Migration via djongo

> `djongo` is a connector that translates Django ORM queries into MongoDB commands. It allows you to keep most of your Django code but replaces the SQL backend.

### Steps Required

**1. Install djongo**

```
djongo==1.3.6
pymongo==3.12.3   # djongo requires pymongo 3.x, NOT 4.x
dnspython          # if using MongoDB Atlas (mongodb+srv://)
```

Remove `psycopg2-binary` and `dj-database-url` if switching to Mongo instead of Postgres.

**2. Change `settings.py` DATABASE block**

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'medicalstore',
        'CLIENT': {
            'host': 'mongodb+srv://<user>:<pass>@cluster.mongodb.net',
        }
    }
}
```

**3. Remove or replace incompatible ORM features**

djongo does not support all Django ORM operations:

| Feature | Status with djongo |
|---------|-------------------|
| Basic CRUD | Supported |
| ForeignKey (stored as embedded ObjectId) | Supported, but JOINs become `$lookup` — slow |
| ManyToMany fields | Not supported — must refactor to embedded documents or manual junction |
| `annotate()` + `aggregate()` | Partially supported — complex aggregations may fail |
| `distinct()` | Limited support |
| `Q()` objects with OR | Partially supported |
| `order_by` on related fields | May break |
| `modeltranslation` | Untested with djongo — high risk of incompatibility |

**4. Replace `modeltranslation` strategy**

`django-modeltranslation` generates extra SQL columns (`name_en`, `name_fr`). This may not work correctly with djongo. Options:
- Store translations as embedded subdocuments in Mongo (requires custom field or refactor)
- Use a different i18n strategy (e.g., store `{"en": "...", "fr": "..."}` in a JSONField)

**5. Migrate existing data**

```bash
# Export from SQLite
python manage.py dumpdata > data.json

# Switch settings.py to djongo, then:
python manage.py migrate       # creates MongoDB collections
python manage.py loaddata data.json
```

Verify all records transferred correctly before removing SQLite.

**6. Remove SQLite file**

- Delete `db.sqlite3`
- Confirm `db.sqlite3` is listed in `.gitignore`

**7. Update `render.yaml`**

- Remove the PostgreSQL service block
- Add MongoDB Atlas connection string as environment variable (e.g. `MONGO_URI`)
- Update database config in `settings.py` to read from environment

**8. Known djongo risks**

- djongo is not actively maintained (last release ~2021) — may have issues with Django 5.x
- `django-modeltranslation` + djongo is an untested combination
- Complex filter chains in `product_list` view may need rewriting
- The `populate_db` management command may need updates for Mongo ObjectId handling

**Alternative recommendation:** If you want MongoDB but need production reliability, consider `mongoengine` with a thin compatibility shim, or switch to PostgreSQL (already configured in `render.yaml`) which avoids all ORM compatibility risk entirely.

---

## 9. Recommended Improvements for a Medicinal Plant E-Commerce Site

### Must-Have (Production Blockers)

- Move all secrets to `.env` file using `django-environ` or `python-decouple`
- Switch `runserver` → `gunicorn` in `render.yaml`
- Fix the IDOR bug on `order_created` view (check `order.user == request.user`)
- Decrement `stock_quantity` when an order is placed; block checkout if stock = 0
- Fix `requirements.txt` — uncomment production dependencies (`gunicorn`, `psycopg2-binary`, etc.)

### High Value for E-Commerce

- **Real payment gateway** — Stripe or PayPal integration; bank transfer alone loses conversions
- **Customer order confirmation email** — currently only admin gets notified
- **Persistent cart** — store cart in DB for logged-in users so it survives session expiry
- **Product image gallery** — multiple images per product (currently only one)
- **Product reviews/ratings** — fields exist on the model but no UI or logic is implemented
- **Wishlist** — standard feature for this product category

### Product Discovery

- **Autocomplete search** — current search is a full-page reload; add HTMX or JS autocomplete
- **Product comparison** — useful for CBD:THC ratio comparisons
- **Related products by strain type** — currently only same-category relations shown
- **"In stock only" filter toggle** — `stock_quantity` field exists but no filter for it
- **Sort options** — price low/high, newest, popularity (no sort UI currently)

### Trust & Compliance (Critical for Medicinal Products)

- **Real age verification** — server-side gate, not just localStorage
- **Lab results / certificates of analysis** — file upload field on Product
- **Batch/lot number tracking** — traceability field on Product
- **Legal disclaimer per country** — currently hardcoded for France
- **Cookie consent that actually blocks trackers** — current implementation is cosmetic only

### Operations & Admin

- **Stock alert emails** — notify admin when `stock_quantity` falls below threshold
- **Order export to CSV** — useful for fulfillment
- **Discount codes / coupon system**
- **Shipping cost calculator** — currently no shipping cost logic in checkout
- **Product import via CSV** — for bulk catalog management
- **Sitemap and robots.txt** — important for SEO of a product catalog site

### Performance

- Move Tailwind and Alpine.js from CDN to bundled assets (Vite or npm build step)
- Add `django-cacheops` or Redis caching for product list queries
- Add `whitenoise` for static file serving (already in requirements, just needs uncommenting)
- Lazy-load product images in the grid

---

## Summary

The codebase is well-structured and feature-complete for an MVP, with good i18n groundwork and a clean filtering system. The most urgent issues are:

1. Exposed credentials in `settings.py` (SMTP password, SECRET_KEY)
2. Broken production deployment config (`runserver` + missing packages in `requirements.txt`)
3. IDOR vulnerability on the `order_created` view
4. Missing stock decrement logic on order creation

The MongoDB/djongo migration is technically feasible but carries real compatibility risk with Django 5.x and `django-modeltranslation`. PostgreSQL (already wired in `render.yaml`) is the safer and better-supported production path.
