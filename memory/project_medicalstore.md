---
name: project-medicalstore
description: Core facts about the medicalstore Django project — stack, deployment, key decisions made
metadata:
  type: project
---

Django 5.2.4 e-commerce site for medicinal/CBD plants. Branch: bikim_app. Deployed to Render.com.

Apps: products, cart (session-based), orders, accounts, pages.

**Key decisions made (2026-06-29):**
- Switched from hardcoded settings to python-decouple reading from .env
- Database: dj-database-url with SQLite local fallback, PostgreSQL on Render
- Whitenoise added for static file serving in production
- render.yaml startCommand fixed to gunicorn
- `pyenv global 3.11.13` is the correct Python to use for `python manage.py` commands

**Why:** Deadline delivery, full security + production hardening in one pass.

**How to apply:** Always use `python` (pyenv 3.11.13 with Django 5.2.4) not `python3` (system Django 4.2) when running manage.py. A .env file must exist at project root.

SiteSettings model (pages app) now has bank transfer fields: bank_name, bank_account_name, bank_account_number, bank_iban, bank_swift_bic — fill these in admin before going live.
