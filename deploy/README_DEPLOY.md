# MOCO EC2 Deployment Guide

This project keeps the current integrated Django + Vue structure:

- repository: `/home/ec2-user/moco`
- Django root: `/home/ec2-user/moco/backend`
- Vue root: `/home/ec2-user/moco/frontend`
- virtualenv: `/home/ec2-user/moco/venv`
- environment file: `/home/ec2-user/moco/.env`
- Gunicorn: `127.0.0.1:8000`
- Nginx config: `/etc/nginx/conf.d/moco.conf`

Django renders the Vue build HTML from:

```bash
/home/ec2-user/moco/backend/templates/home.html
```

Vue build assets are copied to:

```bash
/home/ec2-user/moco/backend/static/frontend/
```

`collectstatic` then publishes static files to:

```bash
/home/ec2-user/moco/backend/staticfiles/
```

## Pre-Push Git Check

Run this before pushing to GitHub:

```bash
git status
git ls-files | grep -Ei '(\.env$|\.pem$|\.key$|backend backup|node_modules|db\.sqlite3)'
```

These files must not be pushed:

- `mocokey.pem`
- `.env`
- `backend backup/`
- `node_modules/`
- `db.sqlite3`
- production logs

`.env.example` should be tracked.

## AWS Security Group

Open only these inbound rules:

```text
SSH   TCP 22   administrator current IP only
HTTP  TCP 80   0.0.0.0/0
HTTPS TCP 443  0.0.0.0/0
```

Do not open port `8000` to the internet. Gunicorn binds only to:

```text
127.0.0.1:8000
```

## First Deployment

Connect to EC2 as `ec2-user`, then run:

```bash
cd /home/ec2-user
git clone git@github.com:hanzeenee/moco.git /home/ec2-user/moco
cd /home/ec2-user/moco
cp .env.example .env
chmod 600 .env
```

Edit `/home/ec2-user/moco/.env` and set real production values. Do not print or commit the file.

For HTTP-only first deployment, these values are expected:

```env
DJANGO_DEBUG=False
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_SECURE_HSTS_SECONDS=0
```

Run setup:

```bash
cd /home/ec2-user/moco
chmod 750 setup_ec2.sh deploy.sh
./setup_ec2.sh
```

If the repository is not cloned yet and you want the script to clone it:

```bash
/home/ec2-user/moco/setup_ec2.sh git@github.com:hanzeenee/moco.git
```

## Redeployment

The redeploy script refuses to overwrite server-side manual changes.

```bash
cd /home/ec2-user/moco
./deploy.sh
```

It runs:

- `git status --porcelain`
- `git pull --ff-only`
- Python dependency install
- Django checks and migrations
- `npm ci`
- Vue lint and build
- `collectstatic`
- Gunicorn restart
- `nginx -t` before Nginx reload
- local HTTP health checks

## Service Checks

```bash
sudo systemctl is-active moco-gunicorn
sudo systemctl is-enabled moco-gunicorn
sudo systemctl is-active nginx
sudo systemctl is-enabled nginx
```

## Logs

```bash
sudo journalctl -u moco-gunicorn -n 100 --no-pager
sudo journalctl -u nginx -n 100 --no-pager
sudo tail -n 100 /var/log/nginx/error.log
sudo tail -n 100 /var/log/nginx/access.log
```

## Port Checks

```bash
sudo ss -lntp
```

Expected:

```text
Nginx: 0.0.0.0:80 or [::]:80
Gunicorn: 127.0.0.1:8000
```

Gunicorn listening on `0.0.0.0:8000` is a configuration error.

## HTTP Checks

```bash
curl -I http://127.0.0.1:8000/
curl -I http://127.0.0.1/
curl -I http://EC2_PUBLIC_IP/
```

## Django Checks

```bash
cd /home/ec2-user/moco/backend
source /home/ec2-user/moco/venv/bin/activate
set -a
source /home/ec2-user/moco/.env
set +a

python manage.py check
python manage.py check --deploy
python manage.py showmigrations
```

`check --deploy` may warn about HTTPS settings until TLS is configured.

## Vue Build Output Checks

```bash
ls -al /home/ec2-user/moco/backend/templates/home.html
ls -al /home/ec2-user/moco/backend/static/frontend/
```

Browser checklist:

- main page uses `/` without `/#/`; old hash links are upgraded in the browser
- refresh
- visitor login/signup/logout controls and `/api/accounts/` routes are absent
- `/api/` requests
- `/admin/`
- CSS
- JavaScript
- images
- Vue history routing: direct entry and refresh on `/lecture`, `/event`, and `/classroom`
- CSRF
- static file 404s
- HTTP 500s

## Nginx Validation

```bash
sudo nginx -t
```

Reload only after validation succeeds:

```bash
sudo systemctl reload nginx
```

## Rollback

Before deployment, record the current commit:

```bash
cd /home/ec2-user/moco
PREVIOUS_COMMIT="$(git rev-parse HEAD)"
echo "$PREVIOUS_COMMIT"
```

The scripts do not run automatic `git reset --hard`.

Manual rollback:

```bash
cd /home/ec2-user/moco
git status
git log --oneline -10
git checkout main
git reset --hard PREVIOUS_COMMIT
./deploy.sh
```

Only do this after confirming there are no manual server changes that need to be preserved.

Database migrations are not automatically rolled back. If a migration has already changed the schema, older code may not be compatible with the current database.

SQLite backup example:

```bash
cd /home/ec2-user/moco
cp backend/db.sqlite3 backend/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

PostgreSQL backup example:

```bash
pg_dump "$DJANGO_DB_NAME" > moco_pg_backup.$(date +%Y%m%d_%H%M%S).sql
```

## HTTPS Changeover

Before HTTPS:

```env
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_SECURE_HSTS_SECONDS=0
```

After HTTPS and proxy headers are confirmed:

```env
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_USE_X_FORWARDED_PROTO=True
```

Also set `DJANGO_CSRF_TRUSTED_ORIGINS` to the HTTPS origin, for example:

```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com
```


## Production SEO endpoints and canonical host

The existing `moco.conf` is the HTTP bootstrap configuration. Once the existing
Let's Encrypt certificate for both hostnames is installed, the versioned
`deploy/moco-https.conf` describes the production HTTPS configuration.
Back up `/etc/nginx/conf.d/moco.conf` before installing it, run `sudo nginx -t`,
and reload Nginx only after validation succeeds. Restore the backup if validation
fails. The certificate and private key remain on the server and are not in Git.

- Canonical public homepage: `https://moconix.com/`.
- HTTP and HTTPS www requests redirect permanently to the canonical HTTPS host
  with status 308, preserving the path, query string, and HTTP method.
- The homepage supplies `Link: <https://moconix.com/>; rel="canonical"`.
  This header applies to the homepage only, including campaign query strings.
- `/robots.txt` returns text/plain and references `/sitemap.xml`.
- `/sitemap.xml` returns XML and lists only the public homepage. Do not add
  administrator pages, API endpoints, the protected library, or old lecture pages.
- Known Vue routes keep their existing behavior; unknown URLs now return 404.
- Library pages keep their authorization checks and send `X-Robots-Tag: noindex`.

Run the routing and existing authorization regression checks before deployment:

```bash
cd backend
python manage.py test dashboard.test_seo utilities.tests utilities.test_licensing utilities.test_indicator_licensing utilities.test_release_catalog --noinput
```

For search registration, use the owner's Google Search Console and Naver Search
Advisor accounts. Verify `https://moconix.com/`, then submit
`https://moconix.com/sitemap.xml` in each service. Registration is a separate
account-side step; publishing robots.txt or a sitemap does not itself register
the website. Keep any genuine verification file or meta tag permanently after
verification. Never invent a verification token or submit under another account.


## Localized homepage initial HTML

`npm run build` produces the regular Vue client bundle and then renders the same
App/HomeView components into `backend/templates/home-ko.html` and `home-en.html`.
These generated templates include the existing public homepage and one WebSite
JSON-LD object identifying MOCONIX / 모코닉스. Both templates reuse the same
client CSS and image assets; do not hand-edit generated snapshots.

Django uses the existing `moconix_language` cookie to choose the initial homepage
HTML (Korean by default), and varies the response by Cookie. Other routes,
including the protected utility library, continue to use the regular app shell.
The browser mounts the existing interactive Vue application after its router is
ready. No Node rendering service runs for visitor requests.

Always run the complete frontend build before restarting Gunicorn so both locale
templates and the client assets are updated together. A normal deployment's build
command already includes this step. The HTML verification tags for Google and
Naver are retained in every generated template.

Additional regression check after the build:

```bash
cd backend
python manage.py test dashboard.test_home_prerender dashboard.test_seo --noinput
```
