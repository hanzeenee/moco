# Utility library access

This is a MOCONIX account-number allowlist, not an INFINOX account/password login or an automatic IB integration. Public member signup remains retired.

- Administrators manage verified accounts at `/admin/utilities/utilityaccessaccount/` after checking their own IB menu.
- Allowed numbers belong in the database only. Do not add customer numbers to migrations, JavaScript, repository fixtures or logs.
- The registration command `python manage.py register_utility_account` reads one number from standard input and activates both library and MT5 program access idempotently, without printing it. Account number is the only required identity; no server name is stored or compared.
- Login is a CSRF-protected POST. Library access uses its own browser-session cookie, separate from the Django administrator session. There is no fixed eight-hour or server-side time limit.
- The HttpOnly, host-only `moconix_library_session` cookie uses `SameSite=Lax`, the configured HTTPS Secure flag and path `/`, with no Expires or Max-Age. The cookie contains only a random 256-bit token; `UtilityBrowserSession` stores its SHA-256 hash and the account relation, never the raw token or account number.
- Refreshes, language changes and home/library navigation retain access while the browser session remains open. Normal browser shutdown removes the cookie. Browser session-restoration features may restore session cookies; websites cannot reliably distinguish restored browser sessions from a browser that stayed open.
- Logging in again, an invalid relogin or the logout endpoint revokes only the currently presented library grant. Other browser grants and administrator session identifiers/expiry are preserved. Old eight-hour Django utility keys are not accepted as authorization after this change.
- Grant rows intentionally have no automatic timeout. Closing a browser removes its client cookie, but cannot reliably notify the server to delete the corresponding row. Account deletion cascades to grants, and account deactivation or explicit logout revokes the presented grant.
- `/utilities` and `/api/utilities/library/` check that the account is still active on every request. Deactivation takes effect immediately on the next protected request.
- The shared AuthBridge and published EX5 files use the same protected download guard. Future private downloads must use this guard rather than public static/media URLs.
- A number alone does not prove ownership. Add stronger verification if the access requirements expand.

Run `python manage.py test utilities accounts --noinput` for the access and legacy-admin regression checks.
