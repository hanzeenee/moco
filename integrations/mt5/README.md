# MOCONIX MT5 startup licensing

This integration checks a compiled EA's actual MT5 login and server against the existing utility access database. It does not connect MT5 directly to the database and does not require a website login.

## Flow and scope

1. `OnInit` reads `ACCOUNT_LOGIN` and `ACCOUNT_SERVER` and makes one HTTPS POST to `https://moconix.com/api/licenses/check/`.
2. The backend requires an active utility account with an exact server match, `ea_enabled=True`, and an active `EAProgram` matching the compiled product ID.
3. A successful response binds protocol, account, server, product and nonce. The MQL5 module compares the complete canonical JSON response.
4. Failure, malformed responses, timeout, missing MT5 URL permission and unavailable infrastructure fail initialization. No offline grace period or cross-run authorization cache exists.
5. Subsequent ticks and trade sends use memory-only account/server guards. There are no periodic network checks. Revoking an account or product affects its next initialization, not an already-running authorized instance.

MT5 can reinitialize an EA after account/timeframe/input changes and terminal restarts. Each initialization authenticates again. Failure does not close existing positions or cancel existing orders; operators must manage them separately.

The reusable `MoconixLicense.mqh` contains licensing only. The customer's uploaded strategy and EX5 are private owner artifacts, not committed here. Distribution is EX5 only; customers do not need the MQ5/header.

## Owner administration / 관리자 운영

- Open `/admin/utilities/utilityaccessaccount/` (existing Django administrator login). Set the customer's exact account number and **MT5 거래 서버명**, enable **이용 허용** and **EA 이용 허용**. A blank server allows the existing web library only, never EA startup.
- Open `/admin/utilities/eaprogram/` to enable/disable program IDs. The supplied private EA uses `moconix-grid-ea-v1`. All EA-enabled accounts can use all active programs; this version does not implement per-product customer entitlements.
- Confirm the customer belongs to your IB through your existing business process before registering. This service does not automatically access INFINOX's IB portal or verify account ownership/IB affiliation.
- Account flags and metadata are private database data. Do not commit customer exports, real customer account numbers, passwords or private EA sources.

For thousands of customers, prepare a private UTF-8 CSV with required columns `account_number,server_name`; optional columns are `is_active,ea_enabled,note`. Use full exact account numbers as text and exact MT5 server names. Boolean values: `true/false/1/0`. Example **fictional** data:

```csv
account_number,server_name,is_active,ea_enabled,note
77112233,Example-MT5Live,true,true,IB checked
77112234,Example-MT5Live,true,false,EA temporarily disabled
```

From `backend/` with the configured server environment and virtualenv, feed the private CSV through standard input:

```sh
python manage.py import_utility_accounts --dry-run < /private/customers.csv
python manage.py import_utility_accounts < /private/customers.csv
```

Dry-run validates without writing. Invalid/duplicate rows reject the whole batch before saving. Import adds/updates listed accounts, preserves optional fields absent from the CSV and leaves unlisted customers unchanged. Limit: 20,000 rows / 2 million text characters per batch. Review CSV flags before import; there is no automatic IB verification. Administration requires server access, not a public upload endpoint.

`configure_ea_license` accepts exactly `account_number,server_name,program_code,program_name` as a JSON object on stdin. It configures an already-active account and creates missing program metadata. It never re-enables a program that an administrator disabled.

## Customer MT5 setup / 고객 설정

1. Copy the supplied `.ex5` to MT5's **File > Open Data Folder > MQL5 > Experts**.
2. Open **Tools > Options > Expert Advisors**. Enable **Allow WebRequest for listed URL** and add `https://moconix.com`.
3. Log in to the registered account on its registered server. Attach the EA to a chart and enable Algo Trading as required by the original strategy.
4. Check the Experts log for `Startup authorization complete`. If rejected, check account/server registration, URL permission and connectivity, then attach again. A successful license does not establish strategy profitability or enable trading permissions by itself.

This online-licensed build does **not** work in Strategy Tester, where MT5 does not support WebRequest. No tester bypass is included. For strategy testing, the owner retains the original private source separately. Ordinary MQL5 indicators cannot directly use WebRequest either; this implementation supports the uploaded EA, not direct network authentication inside indicators.

## Protocol 1

POST JSON, maximum 1024 bytes; no browser session cookies or CSRF token required. The endpoint grants no website session. Browser Origin requests are rejected, and other website endpoints keep their CSRF requirements. Required keys only:

```json
{"protocol":1,"account_number":"77112233","server":"Example-MT5Live","product":"example-ea-v1","nonce":"ABCDEF0123456789ABCDEF0123456789"}
```

Success is HTTP 200 with **exact field order, compact separators, ASCII JSON encoding**, no trailing newline:

```json
{"protocol":1,"allowed":true,"account_number":"77112233","server":"Example-MT5Live","product":"example-ea-v1","nonce":"ABCDEF0123456789ABCDEF0123456789"}
```

The response contract is intentionally strict for MQL5. Changing formatting/order requires coordinated client changes or a new protocol version. Account numbers are canonical positive signed 64-bit decimal strings; server matches are case-sensitive ASCII, maximum 128 characters. Nonce: 32 hex characters. Product: lowercase slug, maximum 64 characters. Rejection returns generic HTTP 403 without disclosing which record failed. Invalid input: 400/413/415; method: 405; rate limit: 429 with Retry-After; cache failure: 503. All responses are no-store.

HTTPS supplies server authenticity. The nonce prevents accepting an unrelated successful response; it is not a secret or proof of terminal ownership. There is no shared master secret embedded in the EX5. As with compiled-client licensing generally, this is access control for the distributed application, not hardware attestation or an absolute anti-tamper guarantee.

Default rate protection: 600 requests/minute/IP/worker using Django's local-memory cache; this is best-effort, not a global distributed quota or DDoS protection. Adjust `MOCONIX_LICENSE_RATE_LIMIT` if necessary. Production nginx overwrites `X-Real-IP`; the application trusts it only for loopback proxy connections. Keep gunicorn private behind that proxy. Request payloads/customer account numbers are not logged by the license view.

## Validation

```sh
python manage.py test utilities accounts --noinput
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
```

Tests cover exact response binding, native requests without sessions, missing/inactive/mismatched permissions, no library grant, malformed JSON, bounds, rate limits/proxy trust, infrastructure failure, admin fields and transactional CSV import. The private EA is compiled separately and its original strategy is checked by removing only the three licensing insertions and comparing with the uploaded original. Compilation and API tests do not replace a live MT5 runtime test. No broker orders are placed during these checks.

Official platform references: [WebRequest](https://www.mql5.com/en/docs/network/webrequest), [account information](https://www.mql5.com/en/docs/constants/environment_state/accountinformation).
