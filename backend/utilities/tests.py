import hashlib
import json
import time
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import UtilityAccessAccount, UtilityBrowserSession
from .views import ACCOUNT_KEY, COOKIE_NAME, EXPIRY_KEY


TOKEN_HEADER_KEY = "HTTP_X_MOCONIX_LIBRARY_TOKEN"


@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"], MOCONIX_UTILITY_DOWNLOAD_DIR="")
class UtilityAccessTests(TestCase):
    def setUp(self):
        self.account = UtilityAccessAccount.objects.create(account_number="77112233")

    def login(self, number="77112233", client=None):
        client = self.client if client is None else client
        response = client.post(reverse("utility-login"), json.dumps({"account_number": number}), content_type="application/json")
        if response.status_code == 200:
            client.defaults[TOKEN_HEADER_KEY] = response.json()["tab_token"]
        else:
            client.defaults.pop(TOKEN_HEADER_KEY, None)
        return response

    def token(self, client=None):
        client = self.client if client is None else client
        return client.defaults[TOKEN_HEADER_KEY]

    @staticmethod
    def digest(token):
        return hashlib.sha256(token.encode("ascii")).hexdigest()

    @staticmethod
    def replay_client(token):
        return Client(**{TOKEN_HEADER_KEY: token})

    def test_document_is_empty_noindex_bootstrap_but_anonymous_data_and_download_are_blocked(self):
        for url in ("/utilities", "/utilities/"):
            with patch("utilities.views.registered_account", side_effect=AssertionError("bootstrap must not read private access")), patch("utilities.views.available_resources", side_effect=AssertionError("bootstrap must not read the catalog")):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "home.html")
            self.assertEqual(response["X-Robots-Tag"], "noindex")
            self.assertIn("no-store", response["Cache-Control"])
            self.assertContains(response, '<div id="app"></div>')
            for private_value in (self.account.account_number, "download_url", "data-prerendered", "UT Bot"):
                self.assertNotContains(response, private_value)
        response = self.client.get(reverse("utility-library-data"))
        self.assertEqual(response.status_code, 401)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(reverse("utility-download", args=["missing"])).status_code, 401)
        self.assertFalse(self.client.get(reverse("utility-session")).json()["authenticated"])

    def test_registered_relogin_rotates_only_presented_tab_grant(self):
        session = self.client.session
        session["unrelated"] = "preserve"
        session.save()
        old_key = session.session_key
        self.assertEqual(self.login().status_code, 200)
        first_token = self.token()
        other = Client()
        self.assertEqual(self.login(client=other).status_code, 200)
        other_token = self.token(other)

        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.token(), first_token)
        self.assertEqual(self.client.session.session_key, old_key)
        self.assertEqual(self.client.session["unrelated"], "preserve")
        self.assertFalse(UtilityBrowserSession.objects.filter(pk=self.digest(first_token)).exists())
        self.assertEqual(self.replay_client(first_token).get(reverse("utility-library-data")).status_code, 401)
        self.assertTrue(other.get(reverse("utility-session")).json()["authenticated"])
        self.assertTrue(UtilityBrowserSession.objects.filter(pk=self.digest(other_token)).exists())
        self.assertEqual(self.client.get(reverse("utility-library-data")).json(), {"items": []})
        self.assertNotIn(self.account.account_number, response.content.decode())

    def test_unknown_inactive_and_malformed_accounts_never_grant_access(self):
        for value, status in [("00000000", 403), ("12x34", 400), ("", 400), (12345, 400), ("1" * 21, 400)]:
            self.assertEqual(self.login(value).status_code, status)
            self.assertNotIn(ACCOUNT_KEY, self.client.session)
            self.assertEqual(UtilityBrowserSession.objects.count(), 0)
        self.account.is_active = False
        self.account.save()
        self.assertEqual(self.login().status_code, 403)

    def test_disabling_account_revokes_presented_grant_on_protected_apis(self):
        targets = [(reverse("utility-library-data"), 401), (reverse("utility-download", args=["missing"]), 401), (reverse("utility-session"), 200)]
        for url, expected_status in targets:
            with self.subTest(url=url):
                self.account.is_active = True
                self.account.save()
                self.assertEqual(self.login().status_code, 200)
                token = self.token()
                self.account.is_active = False
                self.account.save()
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)
                if url == reverse("utility-session"):
                    self.assertFalse(response.json()["authenticated"])
                self.assertNotIn(COOKIE_NAME, response.cookies)
                self.assertFalse(UtilityBrowserSession.objects.filter(pk=self.digest(token)).exists())
                self.account.is_active = True
                self.account.save()
                self.assertEqual(self.replay_client(token).get(reverse("utility-library-data")).status_code, 401)
        self.assertEqual(self.login().status_code, 200)

    def test_login_and_logout_require_csrf_without_revoking_on_csrf_failure(self):
        client = Client(enforce_csrf_checks=True)
        payload = json.dumps({"account_number": self.account.account_number})
        self.assertEqual(client.post(reverse("utility-login"), payload, content_type="application/json").status_code, 403)
        client.get(reverse("utility-session"))
        csrf = client.cookies["csrftoken"].value
        response = client.post(reverse("utility-login"), payload, content_type="application/json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        grant_token = response.json()["tab_token"]
        client.defaults[TOKEN_HEADER_KEY] = grant_token
        self.assertEqual(client.post(reverse("utility-logout")).status_code, 403)
        self.assertTrue(UtilityBrowserSession.objects.filter(pk=self.digest(grant_token)).exists())
        self.assertTrue(client.get(reverse("utility-session")).json()["authenticated"])
        self.assertEqual(client.post(reverse("utility-logout"), HTTP_X_CSRFTOKEN=csrf).status_code, 200)
        self.assertFalse(UtilityBrowserSession.objects.filter(pk=self.digest(grant_token)).exists())

    def test_logout_revokes_presented_token_but_preserves_other_tab_and_django_session(self):
        self.login()
        token = self.token()
        other = Client()
        self.login(client=other)
        session = self.client.session
        session["unrelated"] = "preserve"
        session.save()
        old_key = session.session_key
        response = self.client.post(reverse("utility-logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"authenticated": False})
        self.assertNotIn(COOKIE_NAME, response.cookies)
        self.assertEqual(self.client.session.session_key, old_key)
        self.assertEqual(self.client.session["unrelated"], "preserve")
        self.assertNotIn(ACCOUNT_KEY, self.client.session)
        self.assertFalse(UtilityBrowserSession.objects.filter(pk=self.digest(token)).exists())
        self.assertEqual(self.replay_client(token).get(reverse("utility-library-data")).status_code, 401)
        self.assertTrue(other.get(reverse("utility-session")).json()["authenticated"])

    def test_invalid_relogin_revokes_only_presented_tab_grant(self):
        self.login()
        token = self.token()
        other = Client()
        self.login(client=other)
        response = self.login("00000000")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("tab_token", response.json())
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 401)
        self.assertEqual(self.replay_client(token).get(reverse("utility-library-data")).status_code, 401)
        self.assertTrue(other.get(reverse("utility-session")).json()["authenticated"])

    def test_bad_login_formats_also_revoke_presented_grant(self):
        requests = [("{}", "text/plain", 415), ("{", "application/json", 400),
                    (json.dumps({"account_number": "bad"}), "application/json", 400), (" " * 257, "application/json", 400)]
        for body, content_type, status in requests:
            with self.subTest(content_type=content_type, body=body[:30]):
                self.assertEqual(self.login().status_code, 200)
                token = self.token()
                response = self.client.post(reverse("utility-login"), body, content_type=content_type)
                self.assertEqual(response.status_code, status)
                self.assertNotIn("tab_token", response.json())
                self.assertFalse(UtilityBrowserSession.objects.filter(pk=self.digest(token)).exists())

    def test_registration_command_is_idempotent_and_admin_stays_protected(self):
        for _ in range(2):
            with patch("sys.stdin", StringIO("77112233")):
                call_command("register_utility_account", stdout=StringIO())
        self.assertEqual(UtilityAccessAccount.objects.count(), 1)
        self.assertEqual(self.client.get("/admin/utilities/utilityaccessaccount/").status_code, 302)

    def test_number_only_registration_command_enables_both_library_and_mt5(self):
        self.account.is_active = False
        self.account.ea_enabled = False
        self.account.save()
        with patch("sys.stdin", StringIO(self.account.account_number)):
            call_command("register_utility_account", stdout=StringIO())
        self.account.refresh_from_db()
        self.assertTrue(self.account.is_active)
        self.assertTrue(self.account.ea_enabled)
        self.assertEqual(self.login().status_code, 200)

    def test_language_cookie_never_grants_access_to_private_apis(self):
        for language in ("en", "ko", "unsupported"):
            self.client.cookies["moconix_language"] = language
            response = self.client.get("/utilities")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["X-Robots-Tag"], "noindex")
            self.assertContains(response, '<div id="app"></div>')
            self.assertFalse(self.client.get(reverse("utility-session")).json()["authenticated"])
            self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 401)

    @override_settings(SESSION_COOKIE_AGE=30)
    def test_home_language_changes_and_long_elapsed_time_do_not_expire_tab_grant(self):
        self.login()
        token = self.token()
        self.client.get("/")
        self.client.cookies["moconix_language"] = "en"
        for elapsed in (timedelta(hours=8, seconds=1), timedelta(days=365 * 3)):
            future = timezone.now() + elapsed
            with self.subTest(elapsed=elapsed), patch("time.time", return_value=future.timestamp()), patch("django.utils.timezone.now", return_value=future):
                self.assertTrue(self.client.get(reverse("utility-session")).json()["authenticated"])
                self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 200)
        self.assertEqual(self.token(), token)
        self.assertNotIn(EXPIRY_KEY, self.client.session)

    def test_login_returns_only_tab_token_and_stores_only_its_hash_without_auth_cookie(self):
        for secure in (False, True):
            with self.subTest(secure=secure), self.settings(SESSION_COOKIE_SECURE=secure):
                response = self.login()
                self.assertEqual(set(response.json()), {"authenticated", "tab_token"})
                token = response.json()["tab_token"]
                self.assertRegex(token, r"^[A-Za-z0-9_-]{43}$")
                self.assertNotIn(COOKIE_NAME, response.cookies)
                grant = UtilityBrowserSession.objects.get(pk=self.digest(token))
                self.assertEqual(grant.account_id, self.account.pk)
                self.assertNotEqual(grant.pk, token)
                self.assertNotIn("expires_at", {field.name for field in UtilityBrowserSession._meta.fields})

    def test_missing_forged_and_malformed_headers_never_authorize(self):
        for token in (None, "", "short", "A" * 43, "A" * 44, "+" * 43):
            client = Client() if token is None else self.replay_client(token)
            for url, expected in [(reverse("utility-library-data"), 401), (reverse("utility-download", args=["missing"]), 401), (reverse("utility-session"), 200)]:
                with self.subTest(token=token, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected)
                    self.assertNotIn(COOKIE_NAME, response.cookies)
                    if url == reverse("utility-session"):
                        self.assertFalse(response.json()["authenticated"])
        self.assertEqual(UtilityBrowserSession.objects.count(), 0)

    def test_token_in_cookie_query_body_or_authorization_is_never_a_header_grant(self):
        self.login()
        token = self.token()
        for client in (Client(), Client(HTTP_AUTHORIZATION="Bearer " + token)):
            client.cookies[COOKIE_NAME] = token
            response = client.get(reverse("utility-session"), {"tab_token": token})
            self.assertFalse(response.json()["authenticated"])
            self.assertEqual(response.cookies[COOKIE_NAME].value, "")
            self.assertEqual(response.cookies[COOKIE_NAME]["max-age"], 0)
            self.assertEqual(client.get(reverse("utility-library-data"), {"tab_token": token}).status_code, 401)
            self.assertEqual(client.get(reverse("utility-download", args=["missing"]), {"tab_token": token}).status_code, 401)
            response = client.generic("GET", reverse("utility-library-data"), json.dumps({"tab_token": token}), content_type="application/json")
            self.assertEqual(response.status_code, 401)
        self.assertTrue(self.client.get(reverse("utility-session")).json()["authenticated"])

    def test_legacy_cookie_and_unrelated_header_cannot_revoke_another_tab_grant(self):
        self.login()
        token = self.token()
        for header in (None, "short", "A" * 43):
            for action in ("logout", "invalid-login", "valid-login"):
                with self.subTest(header=header, action=action):
                    fresh = Client() if header is None else self.replay_client(header)
                    fresh.cookies[COOKIE_NAME] = token
                    response = fresh.post(reverse("utility-logout")) if action == "logout" else self.login("00000000" if action == "invalid-login" else self.account.account_number, client=fresh)
                    self.assertEqual(response.status_code, 403 if action == "invalid-login" else 200)
                    self.assertTrue(self.client.get(reverse("utility-session")).json()["authenticated"])

    def test_deleting_or_expiring_django_sessions_does_not_revoke_tab_grant(self):
        for action in ("delete", "expire"):
            with self.subTest(action=action):
                client = Client()
                session = client.session
                session["unrelated"] = "separate"
                session.save()
                self.assertEqual(self.login(client=client).status_code, 200)
                if action == "delete":
                    Session.objects.filter(session_key=session.session_key).delete()
                else:
                    Session.objects.filter(session_key=session.session_key).update(expire_date=timezone.now() - timedelta(seconds=1))
                self.assertTrue(client.get(reverse("utility-session")).json()["authenticated"])
                self.assertEqual(client.get(reverse("utility-library-data")).status_code, 200)

    def test_fresh_tab_with_same_browser_cookies_cannot_restore_library_access(self):
        user = get_user_model().objects.create_superuser(username="browser-admin", email="browser@example.invalid", password="test-browser-password")
        self.client.force_login(user)
        session = self.client.session
        session.set_expiry(timezone.now() + timedelta(days=7))
        session.save()
        self.login()
        fresh = Client()
        fresh.cookies.update(self.client.cookies)
        fresh.cookies[COOKIE_NAME] = self.token()
        self.assertEqual(fresh.get("/admin/").status_code, 200)
        self.assertEqual(fresh.get("/utilities").status_code, 200)
        self.assertFalse(fresh.get(reverse("utility-session")).json()["authenticated"])
        self.assertEqual(fresh.get(reverse("utility-library-data")).status_code, 401)
        self.assertEqual(fresh.get(reverse("utility-download", args=["missing"])).status_code, 401)
        self.assertTrue(self.client.get(reverse("utility-session")).json()["authenticated"])

    def test_legacy_django_utility_keys_alone_never_authorize_after_upgrade(self):
        session = self.client.session
        session[ACCOUNT_KEY] = self.account.pk
        session[EXPIRY_KEY] = time.time() + 365 * 24 * 60 * 60
        session.save()
        self.assertFalse(self.client.get(reverse("utility-session")).json()["authenticated"])
        self.assertEqual(self.client.get("/utilities").status_code, 200)
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 401)
        self.assertEqual(self.client.get(reverse("utility-download", args=["missing"])).status_code, 401)
        self.assertEqual(UtilityBrowserSession.objects.count(), 0)

    def test_library_login_invalid_relogin_and_logout_preserve_admin_identity_and_absolute_expiry(self):
        user = get_user_model().objects.create_superuser(username="preserved-admin", email="admin@example.invalid", password="test-admin-password")
        self.client.force_login(user)
        session = self.client.session
        session["unrelated"] = "preserve"
        session.set_expiry(timezone.now() + timedelta(days=3))
        session.save()
        old_key = session.session_key
        old_expiry = session.get_expiry_date()
        for action in ("login", "invalid", "login", "logout"):
            with self.subTest(action=action):
                session = self.client.session
                session[ACCOUNT_KEY] = self.account.pk
                session[EXPIRY_KEY] = time.time() + 8 * 60 * 60
                session.save()
                response = self.client.post(reverse("utility-logout")) if action == "logout" else self.login("00000000" if action == "invalid" else self.account.account_number)
                self.assertEqual(response.status_code, 403 if action == "invalid" else 200)
                current = self.client.session
                self.assertEqual(current.session_key, old_key)
                self.assertEqual(current["unrelated"], "preserve")
                self.assertEqual(current["_auth_user_id"], str(user.pk))
                self.assertEqual(current.get_expiry_date(), old_expiry)
                self.assertEqual(Session.objects.get(session_key=old_key).expire_date, old_expiry)
                self.assertNotIn(ACCOUNT_KEY, current)
                self.assertNotIn(EXPIRY_KEY, current)
                self.assertEqual(self.client.get("/admin/").status_code, 200)
