# Utility library access

This is a MOCONIX account-number allowlist, not an INFINOX account/password login or an automatic IB integration. Public member signup remains retired.

- Administrators manage verified accounts at `/admin/utilities/utilityaccessaccount/` after checking their own IB menu.
- Allowed numbers belong in the database only. Do not add customer numbers to migrations, JavaScript, repository fixtures or logs.
- The registration command `python manage.py register_utility_account` reads one number from standard input and activates it idempotently, without printing it.
- Login is a CSRF-protected POST. A server-side Django session stores the record ID and an eight-hour access expiry; administrator authentication is preserved.
- `/utilities` and `/api/utilities/library/` check that the account is still active on every request. Deactivation takes effect immediately on the next protected request.
- No utility files are published yet. Future private downloads must check the same access guard and must not be exposed as public static/media URLs.
- A number alone does not prove ownership. Add stronger verification if the access requirements expand.

Run `python manage.py test utilities accounts --noinput` for the access and legacy-admin regression checks.
