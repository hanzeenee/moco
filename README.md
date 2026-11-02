# MOCO

Django + Vue web service.

## Detected Structure

- Django root: `backend`
- Django settings module: `config.settings`
- Django apps: `dashboard`; `accounts` is retained for migration history only.
- Vue root: `frontend`
- Vue build system: Vue CLI
- Vue build output: `backend/templates/home.html`, `backend/static/frontend/`
- API prefix: `/api/`
- Admin path: `/admin/`
- Gunicorn module: `config.wsgi:application`

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On Windows PowerShell, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Frontend

```bash
cd frontend
npm ci
npm run serve
```

The frontend uses same-origin public API paths such as `/api/comments/`. Visitor login, signup, logout, and current-user APIs have been removed. Django admin authentication remains available at `/admin/`.

## Production Build

```bash
cd frontend
npm ci
npm run build
```

The Vue CLI build copies the SPA artifact into Django:

- HTML: `backend/templates/home.html`
- Static assets: `backend/static/frontend/`

Then run Django static collection:

```bash
cd ../backend
python manage.py collectstatic --noinput
```

## EC2 Clone Checklist

```bash
git clone <repository-url>
cd moco
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
```

Set real production values in `.env` on the server. Do not commit `.env`.

```bash
cd frontend
npm ci
npm run build
cd ../backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Production Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_DB_ENGINE`
- `DJANGO_DB_NAME`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SECURE_HSTS_SECONDS`
- `DJANGO_USE_X_FORWARDED_PROTO`

For PostgreSQL, install and configure a supported Django PostgreSQL driver on EC2 before setting `DJANGO_DB_ENGINE=postgresql`.

## AWS Items Not Implemented Here

- EC2 instance creation
- RDS provisioning or data migration
- S3 or CloudFront setup
- HTTPS certificate and Nginx/systemd configuration
- CI/CD

## Pre-Launch Security Checks

- Replace `DJANGO_SECRET_KEY` with a real secret in server environment variables.
- Set `DJANGO_DEBUG=False`.
- Set production `DJANGO_ALLOWED_HOSTS`.
- Set HTTPS origins in `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Enable secure cookies and HSTS only after HTTPS is working.
- Remove local private keys and backup folders from Git tracking before pushing.

## Browser URLs

Vue Router uses HTML5 history mode. Home is `/`; existing pages use `/lecture`, `/event`, and `/classroom` without a `#` fragment. Django's frontend fallback serves the SPA for direct visits and refreshes, while `/api/`, `/admin/`, `/static/`, and `/media/` keep their own handling. Nginx forwards frontend requests to Django.

Existing links such as `/#/` and `/#/lecture` are upgraded to the corresponding history URL in the browser. Root query parameters are kept when the legacy route has no query of its own. Ordinary page anchors are left intact.

## Removed Membership Data

Visitor membership UI and APIs are removed. The accounts.0005_purge_legacy_members migration deletes non-staff, non-superuser accounts, retired profile records/table, non-administrator sessions, and membership-specific permissions/content types and log entries. All staff or superuser accounts, their data, and valid administrator sessions are preserved. Django admin authentication remains available at /admin/.

Back up the database before this irreversible data migration. Keep the accounts migration history installed for consistent upgrades; no runtime membership model or API remains.

## Home Service Menu

The right-hand home panel has five equal service cards. Confirmed external destinations are centralized in frontend/src/data/serviceLinks.js. Development/reviews open KakaoTalk/Kmong in a new tab; INFINOX and business details use dialogs. The INFINOX referral URL is maintained separately in frontend/src/data/infinoxGuide.js, so its card continues to open the guide.

## Utility Library and Languages

Free utilities use the backend registered-account allowlist described in backend/utilities/README.md. Logging in opens /utilities in the same tab. Returning home does not log out: authenticated clients can reopen the service directly for the remainder of their original eight-hour grant. A small logout control remains in the library. This verifies an allowlisted account number, not actual ownership through INFINOX.

The header's KR/EN capsule and its dropdown align with the right edge of the home service list; YouTube sits immediately to its left. Korean is the default. An explicit choice is kept in localStorage and the non-sensitive moconix_language cookie, and updates html[lang]. No automatic browser-language selection or external translation service is used. Public frontend copy is maintained in frontend/src/i18n/messages.mjs. The protected Django denial page honors the same explicit cookie; admin pages and external platform pages keep their own language settings. Switching languages does not restart the EA demo or change library authorization.

Run npm run test:language and npm run test:simulation from frontend; run python manage.py test utilities accounts from backend.
