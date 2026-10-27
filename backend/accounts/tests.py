from django.apps import apps
from django.contrib import admin
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from django.urls import resolve


@override_settings(SECURE_SSL_REDIRECT=False)
class RetiredMembershipTests(SimpleTestCase):
    def test_public_membership_endpoints_are_gone(self):
        for endpoint in ("signup", "login", "logout", "me"):
            for prefix in ("/api/accounts/", "/accounts/"):
                for method in (self.client.get, self.client.post):
                    with self.subTest(endpoint=endpoint, prefix=prefix, method=method.__name__):
                        self.assertEqual(method(f"{prefix}{endpoint}/").status_code, 404)

    def test_profile_is_not_a_runtime_or_admin_model(self):
        with self.assertRaises(LookupError):
            apps.get_model("accounts", "Profile")
        self.assertFalse(any(model._meta.app_label == "accounts" for model in admin.site._registry))

    def test_admin_still_requires_its_own_authentication(self):
        self.assertEqual(resolve("/admin/login/").url_name, "login")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)


class RetireProfileMigrationTests(TransactionTestCase):
    def test_existing_records_survive_profile_retirement(self):
        previous = [("accounts", "0003_profile_name")]
        latest = [("accounts", "0004_retire_profile")]
        executor = MigrationExecutor(connection)
        executor.migrate(previous)
        historical_apps = executor.loader.project_state(previous).apps
        user = historical_apps.get_model("auth", "User").objects.create(username="retirement-test", password="!")
        profile = historical_apps.get_model("accounts", "Profile").objects.create(
            user_id=user.pk, name="Preserved profile", birth="000101", phone="test-only"
        )
        try:
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
            with self.assertRaises(LookupError):
                executor.loader.project_state(latest).apps.get_model("accounts", "Profile")
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, user_id FROM accounts_profile WHERE id = %s", [profile.pk])
                self.assertEqual(cursor.fetchone(), ("Preserved profile", user.pk))
                cursor.execute("SELECT username FROM auth_user WHERE id = %s", [user.pk])
                self.assertEqual(cursor.fetchone(), ("retirement-test",))
                constraints = connection.introspection.get_constraints(cursor, "accounts_profile")
                self.assertFalse(any(item["foreign_key"] for item in constraints.values()))
            # The retired archive must not interfere with normal administrator operations.
            apps.get_model("auth", "User").objects.get(pk=user.pk).delete()
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM accounts_profile WHERE id = %s", [profile.pk])
                self.assertEqual(cursor.fetchone(), ("Preserved profile",))
        finally:
            MigrationExecutor(connection).migrate(latest)
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM accounts_profile WHERE id = %s", [profile.pk])
