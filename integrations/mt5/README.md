# MOCONIX MT5 startup licensing

This integration checks a compiled EA's actual MT5 account number against the existing utility access database. It does not connect MT5 directly to the database and does not require a website login.

## Flow and scope

1. `OnInit` reads `ACCOUNT_LOGIN` and `ACCOUNT_SERVER` and makes one HTTPS POST to `https://moconix.com/api/licenses/check/`.
2. The backend requires an active utility account matching the account number, `ea_enabled=True`, and an active `EAProgram` matching the compiled product ID.
3. A successful response binds protocol, account, server, product and nonce. The MQL5 module compares the complete canonical JSON response. The automatically supplied server value stays in the unchanged wire protocol and local session-binding checks for compatibility with existing EX5 files; any valid server name can authorize the same registered account number. Operators do not collect or store server names, and existing EX5 files do not need replacement for this policy change.
4. Failure, malformed responses, timeout, missing MT5 URL permission and unavailable infrastructure fail initialization. No offline grace period or cross-run authorization cache exists.
5. Subsequent ticks and trade sends use memory-only account/server guards. There are no periodic network checks. Revoking an account or product affects its next initialization, not an already-running authorized instance.

MT5 can reinitialize an EA after account/timeframe/input changes and terminal restarts. Each initialization authenticates again. Failure does not close existing positions or cancel existing orders; operators must manage them separately.

The reusable `MoconixLicense.mqh` contains licensing only. The customer's uploaded strategy and EX5 are private owner artifacts, not committed here. Distribution is EX5 only; customers do not need the MQ5/header.

## Owner administration / 관리자 운영

- Open `/admin/utilities/utilityaccessaccount/` (existing Django administrator login). Enter only the customer's exact account number; **이용 허용** and **MT5 프로그램 이용 허용** default to enabled. There is no server-name database field, registration requirement or server allowlist. The single-number registration command enables both permissions.
- Open `/admin/utilities/eaprogram/` to enable/disable program IDs. The supplied private EA uses `moconix-grid-ea-v1`. All MT5-enabled accounts can use all active programs of the matching type; this version does not implement per-product customer entitlements.
- Confirm the customer belongs to your IB through your existing business process before registering. This service does not automatically access INFINOX's IB portal or verify account ownership/IB affiliation.
- Account flags and metadata are private database data. Do not commit customer exports, real customer account numbers, passwords or private EA sources.

For thousands of customers, prepare a private UTF-8 CSV with required column `account_number`; optional columns are `is_active,ea_enabled,note`. Use full exact account numbers as text. No server name is required. Boolean values: `true/false/1/0`. Example **fictional** data:

```csv
account_number,is_active,ea_enabled,note
77112233,true,true,IB checked
77112234,true,false,EA temporarily disabled
```

From `backend/` with the configured server environment and virtualenv, feed the private CSV through standard input:

```sh
python manage.py import_utility_accounts --dry-run < /private/customers.csv
python manage.py import_utility_accounts < /private/customers.csv
```

Dry-run validates without writing. Invalid/duplicate rows reject the whole batch before saving. Import adds/updates listed accounts, preserves optional fields absent from the CSV and leaves unlisted customers unchanged. Limit: 20,000 rows / 2 million text characters per batch. Review CSV flags before import; there is no automatic IB verification. Administration requires server access, not a public upload endpoint.

`configure_ea_license` accepts exactly `account_number,program_code,program_name` as a JSON object on stdin. It configures an already-active account and creates missing program metadata. It never re-enables a program that an administrator disabled.

## Customer MT5 setup / 고객 설정

1. Copy the supplied `.ex5` to MT5's **File > Open Data Folder > MQL5 > Experts**.
2. Open **Tools > Options > Expert Advisors**. Enable **Allow WebRequest for listed URL** and add `https://moconix.com`.
3. Log in to the registered MT5 account number. Attach the EA to a chart and enable Algo Trading as required by the original strategy.
4. Check the Experts log for `Startup authorization complete`. If rejected, check account registration, URL permission and connectivity, then attach again. A successful license does not establish strategy profitability or enable trading permissions by itself.

This online-licensed build does **not** work in Strategy Tester, where MT5 does not support WebRequest. No tester bypass is included. For strategy testing, the owner retains the original private source separately. Ordinary MQL5 indicators cannot directly use WebRequest. The separate signed AuthBridge flow below supports indicator initialization without adding networking or DLLs to the indicator.

## Protocol 1

POST JSON, maximum 1024 bytes; no browser session cookies or CSRF token required. The endpoint grants no website session. Browser Origin requests are rejected, and other website endpoints keep their CSRF requirements. Required keys only:

```json
{"protocol":1,"account_number":"77112233","server":"Example-MT5Live","product":"example-ea-v1","nonce":"ABCDEF0123456789ABCDEF0123456789"}
```

Success is HTTP 200 with **exact field order, compact separators, ASCII JSON encoding**, no trailing newline:

```json
{"protocol":1,"allowed":true,"account_number":"77112233","server":"Example-MT5Live","product":"example-ea-v1","nonce":"ABCDEF0123456789ABCDEF0123456789"}
```

The response contract is intentionally strict for MQL5. Changing formatting/order requires coordinated client changes or a new protocol version. Account numbers are canonical positive signed 64-bit decimal strings; the legacy server field is bounded ASCII response-binding metadata (maximum 128 characters), not a database permission or registration criterion. Nonce: 32 hex characters. Product: lowercase slug, maximum 64 characters. Rejection returns generic HTTP 403 without disclosing which record failed. Invalid input: 400/413/415; method: 405; rate limit: 429 with Retry-After; cache failure: 503. All responses are no-store.

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

## Indicator authorization via AuthBridge (protocol 2)

`MOCONIX_AuthBridge.mq5` is a non-trading EA. Keep exactly one helper on a separate chart without another EA. The indicator includes `MoconixIndicatorLicense.mqh`, which includes `MoconixAuthProtocol.mqh`. The private RSIArrow formula/source and compiled EX5 files are owner artifacts and must not be committed here.

1. Each indicator initialization reads the actual terminal account/server and creates a fresh 32-hex nonce, including an atomic terminal-local initialization sequence.
2. The indicator writes a bounded, atomic request in its own terminal's `MQL5/Files/MoconixAuth/` sandbox. A custom chart event contains only the nonce; MT5 limits string event parameters to 63 characters. While the helper is attaching, a failed or lost local event does not deny authorization. The indicator retries only local notification while the same unconsumed request exists. The helper consumes that file before its one HTTPS check; the indicator never republishes a consumed request or treats event delivery as a grant.
3. The helper checks the actual account/server, consumes the request once, and sends one HTTPS POST to `/api/licenses/indicator/`. Its timeout is 5 seconds, with no HTTP retries or periodic checks.
4. The backend requires an active registered account number with MT5 permission, plus an active `indicator` program. It signs an initialization-bound grant using RSA-PSS/SHA256, 2048-bit RSA, exponent 65537 and a 32-byte salt.
5. The indicator independently verifies the full message and signature using its embedded public key. Unsigned, altered, replayed, wrong-account, wrong-server and wrong-product responses are rejected. The helper cannot manufacture a grant. The chart becoming visible as an EA host is not proof that its initialization or event handler is ready. Mailboxes are removed after resolution/deinitialization; authorization is not cached across runs.
6. A local startup timer waits for the helper without a deadline and without HTTP requests. The indicator and helper may be attached in either order; a later helper automatically triggers the single initialization request. The timer stops after authorization and initial local chart-data preparation, or denial. Subsequent calculations use a memory-only account/server guard. An account change latches denial until reinitialization.

Protocol 2 requests use the same five JSON fields as protocol 1, with `protocol: 2`. Success is text/plain ASCII, exactly:

```text
MOCONIX-INDICATOR-1|77112233|Example-MT5Live|example-indicator-v1|ABCDEF0123456789ABCDEF0123456789
<512 uppercase hex characters: RSA-PSS signature of the first line>
```

There is one LF between the message and signature, with no trailing newline. All fields, including the nonce, are signed. Rejection grants no browser session. Protocol 1 remains unchanged for the existing EA.

### Deployment and private files

- Install `backend/requirements.txt`, including `cryptography>=46,<47`; run migrations.
- `MOCONIX_INDICATOR_SIGNING_KEY` points to an RSA-2048 PEM private key outside the repository/static/media roots. Restrict its directory to the service owner (0700) and key to 0600. The corresponding public modulus is compiled into `MoconixAuthProtocol.mqh`. Rotating the key requires coordinated recompilation/distribution; never export the private key to clients or commit it.
- `MOCONIX_UTILITY_DOWNLOAD_DIR` points to an owner-only private directory containing the shared `MOCONIX_AuthBridge.ex5`. Do not serve that directory through nginx, Django static or media. Only fixed catalog IDs are accepted by the session-guarded download endpoint; no source/key files are cataloged. RSIArrow is an owner-only test artifact, not a published library item: its catalog entry and download route are intentionally unavailable. Publishing an indicator later requires explicit owner instruction. The shared helper download does not depend on the private test product being enabled.
- Register `moconix-rsi-arrow-v1` as type `indicator`, active. Existing program rows default to type `ea`. Do not overwrite an administrator's disabled program or customer flags.
- Website library access still uses its existing registered-account session. File download permission does not grant MT5 authorization; the EX5 verifies the terminal's actual account/server on initialization.

### Owner test indicator setup (not published)

Copy `MOCONIX_RSIArrow.ex5` to `MQL5/Indicators` and `MOCONIX_AuthBridge.ex5` to `MQL5/Experts`. Keep file names unchanged. Allow `https://moconix.com` under Tools > Options > Expert Advisors > WebRequest. Sign in to the registered account number, refresh Navigator and attach the helper to a separate chart and the indicator to the desired chart, in either order. An indicator attached first waits locally for the helper without a time limit. Keep the helper chart open. No DLLs, orders or Algo Trading trading permission are required by the helper. This online indicator build does not run in Strategy Tester.

The owner tests the private indicator using the locally supplied two EX5 files. No indicator is currently published on the website. When the owner explicitly publishes a product later, customer accounts can use the same EX5 build; only the server database changes when customers are added. Account/program revocation affects the next initialization, not an already-authorized running instance. The database is operator managed; there is no automatic broker/IB portal integration or proof of account ownership in the account-number website login.

### Additional validation

The backend suite verifies signed grants independently, wrong identity/type/permissions, unavailable signing infrastructure, protected downloads and session/logout behavior. Private native MT5 mathematical self-tests verify the exact MQL RSA-PSS verifier and client state machine (indefinite helper waiting, both attachment orders, failed/lost local delivery before readiness, temporary mailbox failure, one server request, account-change latch, denial). Those tests use fake account identities only in isolated test harnesses; production headers/binaries contain no tester bypass. Both customer EX5 builds compile with zero errors and warnings. Tests place no broker orders and do not replace a customer live-chart setup check.

Official references: [custom chart events](https://www.mql5.com/en/docs/eventfunctions/eventchartcustom), [RSA-PSS](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/).
