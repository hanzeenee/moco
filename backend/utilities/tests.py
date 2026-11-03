import json
import time
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import UtilityAccessAccount
from .views import ACCOUNT_KEY, EXPIRY_KEY


@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"], MOCONIX_UTILITY_DOWNLOAD_DIR="")
class UtilityAccessTests(TestCase):
    def setUp(self):
        self.account = UtilityAccessAccount.objects.create(account_number="77112233")

    def login(self, number="77112233"):
        return self.client.post(reverse("utility-login"), json.dumps({"account_number": number}), content_type="application/json")

    def test_anonymous_direct_page_and_data_are_blocked(self):
        self.assertEqual(self.client.get("/utilities").status_code, 403)
        self.assertEqual(self.client.get("/utilities/").status_code, 403)
        response = self.client.get(reverse("utility-library-data"))
        self.assertEqual(response.status_code, 401)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertFalse(self.client.get(reverse("utility-session")).json()["authenticated"])

    def test_registered_login_rotates_session_and_allows_empty_library(self):
        session = self.client.session
        session["unrelated"] = "preserve"
        session.save()
        old_key = session.session_key
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.client.session.session_key, old_key)
        self.assertEqual(self.client.session["unrelated"], "preserve")
        self.assertEqual(self.client.get("/utilities").status_code, 200)
        self.assertEqual(self.client.get(reverse("utility-library-data")).json(), {"items": []})
        self.assertNotIn(self.account.account_number, response.content.decode())

    def test_unknown_inactive_and_malformed_accounts_never_grant_access(self):
        for value, status in [("00000000", 403), ("12x34", 400), ("", 400), (12345, 400), ("1" * 21, 400)]:
            self.assertEqual(self.login(value).status_code, status)
            self.assertNotIn(ACCOUNT_KEY, self.client.session)
        self.account.is_active = False
        self.account.save()
        self.assertEqual(self.login().status_code, 403)

    def test_disabling_or_expiring_account_revokes_existing_access(self):
        self.login()
        self.account.is_active = False
        self.account.save()
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 401)
        self.account.is_active = True
        self.account.save()
        self.login()
        session = self.client.session
        session[EXPIRY_KEY] = time.time() - 1
        session.save()
        self.assertEqual(self.client.get("/utilities").status_code, 403)

    def test_login_and_logout_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        payload = json.dumps({"account_number": self.account.account_number})
        self.assertEqual(client.post(reverse("utility-login"), payload, content_type="application/json").status_code, 403)
        client.get(reverse("utility-session"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(reverse("utility-login"), payload, content_type="application/json", HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.assertEqual(client.post(reverse("utility-logout")).status_code, 403)

    def test_logout_removes_only_library_access_and_requires_login_again(self):
        self.login()
        session = self.client.session
        session["unrelated"] = "preserve"
        session.save()
        self.assertEqual(self.client.post(reverse("utility-logout")).status_code, 200)
        self.assertEqual(self.client.session["unrelated"], "preserve")
        self.assertNotIn(ACCOUNT_KEY, self.client.session)
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 401)

    def test_invalid_relogin_clears_previous_grant(self):
        self.login()
        self.assertEqual(self.login("00000000").status_code, 403)
        self.assertEqual(self.client.get(reverse("utility-library-data")).status_code, 401)

    def test_registration_command_is_idempotent_and_admin_stays_protected(self):
        for _ in range(2):
            with patch("sys.stdin", StringIO("77112233")):
                call_command("register_utility_account", stdout=StringIO())
        self.assertEqual(UtilityAccessAccount.objects.count(), 1)
        self.assertEqual(self.client.get("/admin/utilities/utilityaccessaccount/").status_code, 302)

    def test_language_preference_translates_denial_without_granting_access(self):
        self.client.cookies["moconix_language"] = "en"
        response = self.client.get("/utilities")
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Library login required", status_code=403)
        self.assertContains(response, 'lang="en"', status_code=403)
        self.assertFalse(self.client.get(reverse("utility-session")).json()["authenticated"])
        self.client.cookies["moconix_language"] = "unsupported"
        response = self.client.get("/utilities")
        self.assertContains(response, "자료실 로그인이 필요합니다", status_code=403)

    def test_home_revisit_and_language_changes_preserve_original_eight_hour_grant(self):
        self.login()
        expires = self.client.session[EXPIRY_KEY]
        self.assertAlmostEqual(expires - time.time(), 8 * 60 * 60, delta=2)
        self.client.get("/")
        self.client.cookies["moconix_language"] = "en"
        self.assertTrue(self.client.get(reverse("utility-session")).json()["authenticated"])
        self.assertEqual(self.client.get("/utilities").status_code, 200)
        self.assertEqual(self.client.session[EXPIRY_KEY], expires)
