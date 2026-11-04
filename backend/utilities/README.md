# Utility library access

This is a MOCONIX account-number allowlist, not an INFINOX account/password login or an automatic IB integration. Public member signup remains retired.

- Administrators manage verified accounts at `/admin/utilities/utilityaccessaccount/` after checking their own IB menu.
- Allowed numbers belong in the database only. Do not add customer numbers to migrations, JavaScript, repository fixtures or logs.
- The registration command `python manage.py register_utility_account` reads one number from standard input and activates both library and MT5 program access idempotently, without printing it. Account number is the only required identity; no server name is stored or compared.
- Login is a CSRF-protected POST. A successful response returns an opaque `tab_token`, kept only in the current tab's `sessionStorage`. There is no fixed eight-hour or server-side time limit.
- Protected library/session requests and EX5 downloads require `X-Moconix-Library-Token`. Cookies, URL parameters, request bodies and Django administrator sessions are never library grants. The frontend downloads EX5 files with an authenticated request, keeping tokens out of URLs.
- `UtilityBrowserSession` stores only the SHA-256 hash of the random 256-bit token and its account relation. The raw token and customer number are not stored in this grant table. The previous browser-wide `moconix_library_session` cookie is expired when presented and never used for authorization or grant revocation.
- Refreshes, language changes and home/library navigation retain access in the same tab. After an ordinary tab close, a fresh tab has no token and must log in again. Browser restore or duplicate-tab features may preserve or copy `sessionStorage`; a restored tab is not guaranteed to behave like a fresh tab.
- Logging in again, an invalid relogin or the logout endpoint revokes only the grant presented in the current request's token header. Requests without that header do not revoke another tab's grant. Other tab grants and administrator session identifiers/expiry are preserved. Old eight-hour Django utility keys are not accepted as authorization.
- Grant rows intentionally have no automatic timeout. Closing a tab clears its client storage but cannot reliably notify the server to delete the corresponding row. Account deletion cascades to grants, and account deactivation or explicit logout revokes the presented grant.
- `/utilities` and `/utilities/` serve only the empty, noindex, non-cacheable Vue bootstrap so same-tab refreshes can restore the token locally. The bootstrap contains no account details, private catalog or download payloads. `/api/utilities/library/`, `/api/utilities/session/` and every private download validate the header grant and active account. Deactivation takes effect on the next protected API request.
- The shared AuthBridge and published EX5 files use the same protected download guard. Future private downloads must use this guard rather than public static/media URLs.
- A number alone does not prove ownership. Add stronger verification if the access requirements expand.

Run `python manage.py test utilities accounts --noinput` for the access and legacy-admin regression checks.
