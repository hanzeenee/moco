"""Native MT5 licensing contract and account administration regressions."""
import json
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command, CommandError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import EAProgram, UtilityAccessAccount
from .views import ACCOUNT_KEY


@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"], MOCONIX_LICENSE_RATE_LIMIT=600)
class LicenseTests(TestCase):
    def setUp(self):
        cache.clear()
        self.account = UtilityAccessAccount.objects.create(account_number="77112233")
        self.program = EAProgram.objects.create(code="example-ea-v1", name="Example EA")
        self.payload = {"protocol": 1, "account_number": self.account.account_number,
                        "server": "Example-MT5Live", "product": self.program.code, "nonce": "ABCDEF0123456789" * 2}
        self.url = reverse("ea-license-check")

    def post(self, payload=None, client=None, **extra):
        return (client or self.client).post(self.url, json.dumps(self.payload if payload is None else payload),
                                           content_type="application/json", **extra)

    def test_native_request_has_exact_bound_response_without_session_or_browser_grant(self):
        native = Client(enforce_csrf_checks=True)
        response = self.post(client=native)
        self.assertEqual(response.status_code, 200)
        expected = {"protocol": 1, "allowed": True, **{k: self.payload[k] for k in ("account_number", "server", "product", "nonce")}}
        self.assertEqual(response.content, json.dumps(expected, separators=(",", ":")).encode())
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertFalse(response.cookies)
        self.assertNotIn(ACCOUNT_KEY, native.session)
        self.assertEqual(native.get("/utilities").status_code, 200)
        self.assertEqual(native.get(reverse("utility-library-data")).status_code, 401)

    def test_unknown_account_and_program_share_generic_denial(self):
        denials = []
        for key, value in [("account_number", "77112234"), ("product", "missing-ea")]:
            response = self.post({**self.payload, key: value})
            self.assertEqual(response.status_code, 403)
            denials.append(response.content)
            self.assertNotIn(self.account.account_number.encode(), response.content)
        self.assertEqual(len(set(denials)), 1)

    def test_number_only_registration_authorizes_ea_from_any_valid_server(self):
        self.assertNotIn("server_name", {field.name for field in UtilityAccessAccount._meta.fields})
        for server in ["Example-MT5Live", "OtherBroker-Live", "Example-MT5Demo", "example-MT5Live"]:
            response = self.post({**self.payload, "server": server})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["server"], server)
        response = self.client.post(reverse("utility-login"), json.dumps({"account_number": self.account.account_number}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.client.defaults["HTTP_X_MOCONIX_LIBRARY_TOKEN"] = response.json()["tab_token"]
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 200)

    def test_account_and_program_flags_are_enforced_independently(self):
        for field, value in [("is_active", False), ("ea_enabled", False)]:
            previous = getattr(self.account, field)
            setattr(self.account, field, value)
            self.account.save()
            self.assertEqual(self.post().status_code, 403)
            setattr(self.account, field, previous)
            self.account.save()
        self.program.is_active = False
        self.program.save()
        self.assertEqual(self.post().status_code, 403)

    def test_revocation_is_seen_at_next_startup_and_does_not_revoke_library(self):
        self.assertEqual(self.post().status_code, 200)
        self.account.ea_enabled = False
        self.account.save()
        self.assertEqual(self.post().status_code, 403)
        response = self.client.post(reverse("utility-login"), json.dumps({"account_number": self.account.account_number}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.client.defaults["HTTP_X_MOCONIX_LIBRARY_TOKEN"] = response.json()["tab_token"]
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 200)

    def test_malformed_or_ambiguous_payload_never_authorizes(self):
        for key, values in {"protocol": [True, 2, "1"], "account_number": [77112233, "0", "077112233", "9223372036854775808", "1\n"],
                            "server": [None, "", "x" * 129, "Example\nServer"], "product": ["", "X", "x" * 65], "nonce": ["", "f" * 31, "g" * 32]}.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    self.assertEqual(self.post({**self.payload, key: value}).status_code, 400)
        for payload in [[], None, {**self.payload, "extra": 1}, {k: v for k, v in self.payload.items() if k != "nonce"}]:
            raw = json.dumps(payload)
            self.assertEqual(self.client.post(self.url, raw, content_type="application/json").status_code, 400)
        duplicate = json.dumps(self.payload)[:-1] + ',"protocol":1}'
        self.assertEqual(self.client.post(self.url, duplicate, content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(self.url, b"\xff", content_type="application/json").status_code, 400)

    def test_transport_rules_preserve_other_csrf_protection(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(self.client.post(self.url, "{}", content_type="text/plain").status_code, 415)
        self.assertEqual(self.client.post(self.url, " " * 1025, content_type="application/json").status_code, 413)
        self.assertEqual(self.post(HTTP_ORIGIN="https://moconix.com").status_code, 403)
        native = Client(enforce_csrf_checks=True)
        self.assertEqual(native.post(reverse("utility-login"), "{}", content_type="application/json").status_code, 403)

    @override_settings(MOCONIX_LICENSE_RATE_LIMIT=2)
    def test_rate_limit_trusts_only_local_proxy_and_returns_retry_after(self):
        for ip in ["198.51.100.1", "198.51.100.2"]:
            self.assertEqual(self.post(REMOTE_ADDR="203.0.113.9", HTTP_X_REAL_IP=ip).status_code, 200)
        response = self.post(REMOTE_ADDR="203.0.113.9", HTTP_X_REAL_IP="198.51.100.3")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "60")
        # Real local nginx connections may have distinct client IPs.
        for ip in ["198.51.100.4", "198.51.100.5"]:
            self.assertEqual(self.post(REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP=ip).status_code, 200)

    def test_cache_failure_fails_closed(self):
        with patch("utilities.licensing.cache.add", side_effect=RuntimeError("offline")):
            self.assertEqual(self.post().status_code, 503)

    def test_authenticated_admin_can_register_account_without_server_and_manage_flags(self):
        owner = get_user_model().objects.create_superuser(username="license-test-admin", password="test-password-only")
        self.client.force_login(owner)
        response = self.client.get(reverse("admin:utilities_utilityaccessaccount_change", args=[self.account.pk]))
        self.assertNotContains(response, 'name="server_name"')
        self.assertContains(response, 'name="account_number"')
        self.assertContains(response, 'name="ea_enabled"')
        self.assertEqual(self.client.get(reverse("admin:utilities_eaprogram_changelist")).status_code, 200)


@override_settings(SECURE_SSL_REDIRECT=False)
class LicenseImportTests(TestCase):
    def run_import(self, text, **options):
        with patch("sys.stdin", StringIO(text)):
            call_command("import_utility_accounts", stdout=StringIO(), **options)

    def test_bulk_import_updates_preserves_unspecified_fields_and_is_idempotent(self):
        existing = UtilityAccessAccount.objects.create(account_number="77112233", note="keep", ea_enabled=False)
        csv = "\ufeffaccount_number\n77112233\n77112234\n"
        self.run_import(csv, dry_run=True)
        self.assertEqual(UtilityAccessAccount.objects.count(), 1)
        for _ in range(2):
            self.run_import(csv)
        existing.refresh_from_db()
        self.assertEqual(existing.note, "keep")
        self.assertFalse(existing.ea_enabled)
        self.assertEqual(UtilityAccessAccount.objects.count(), 2)

    def test_invalid_duplicate_or_malformed_csv_rolls_back_entire_batch(self):
        for rows in ["77112233\n77112233\n", "77112233\ninvalid\n", '"unterminated', "77112233,unexpected\n"]:
            with self.subTest(rows=rows), self.assertRaises(CommandError):
                self.run_import("account_number\n" + rows)
            self.assertEqual(UtilityAccessAccount.objects.count(), 0)
        with self.assertRaises(CommandError):
            self.run_import('"unterminated')

    def test_configure_requires_existing_active_customer_and_preserves_disabled_program(self):
        payload = {"account_number": "77112233", "program_code": "example-ea", "program_name": "Example EA"}
        with patch("sys.stdin", StringIO(json.dumps(payload))), self.assertRaises(CommandError):
            call_command("configure_ea_license", stdout=StringIO())
        self.assertEqual(EAProgram.objects.count(), 0)
        customer = UtilityAccessAccount.objects.create(account_number=payload["account_number"])
        for _ in range(2):
            with patch("sys.stdin", StringIO(json.dumps(payload))):
                call_command("configure_ea_license", stdout=StringIO())
        self.assertEqual(EAProgram.objects.count(), 1)
        EAProgram.objects.update(is_active=False)
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            call_command("configure_ea_license", stdout=StringIO())
        self.assertFalse(EAProgram.objects.get().is_active)
        customer.refresh_from_db()
        self.assertTrue(customer.ea_enabled)
        payload["program_name"] = ""
        with patch("sys.stdin", StringIO(json.dumps(payload))), self.assertRaises(CommandError):
            call_command("configure_ea_license", stdout=StringIO())
