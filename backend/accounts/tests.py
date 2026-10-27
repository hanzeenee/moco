from importlib import import_module
from datetime import timedelta

from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
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


class PurgeLegacyMembershipTests(TransactionTestCase):
    def test_purge_removes_members_and_preserves_all_administrator_types(self):
        User = apps.get_model("auth", "User")
        Session = apps.get_model("sessions", "Session")
        ContentType = apps.get_model("contenttypes", "ContentType")
        Permission = apps.get_model("auth", "Permission")
        LogEntry = apps.get_model("admin", "LogEntry")
        admins = [
            User.objects.create(username="staff", is_staff=True, password="retained-hash"),
            User.objects.create(username="superuser", is_superuser=True, password="retained-hash"),
            User.objects.create(username="inactive-staff", is_staff=True, is_active=False, password="retained-hash"),
        ]
        members = [
            User.objects.create(username="former-member"),
            User.objects.create(username="inactive-member", is_active=False),
        ]
        original_admins = list(User.objects.filter(pk__in=[u.pk for u in admins]).order_by("pk").values())
        historical_apps = MigrationExecutor(connection).loader.project_state([("accounts", "0003_profile_name")]).apps
        Profile = historical_apps.get_model("accounts", "Profile")
        with connection.schema_editor() as editor:
            editor.create_model(Profile)
        for member in members:
            Profile.objects.create(user_id=member.pk, name="Disposable member", birth="000101", phone="test-only")

        store = SessionStore()
        for key, user in (("admin-session", admins[0]), ("member-session", members[0]), ("anonymous-session", None)):
            Session.objects.create(
                session_key=key,
                session_data=store.encode({"_auth_user_id": str(user.pk)} if user else {}),
                expire_date=timezone.now() + timedelta(days=1),
            )
        profile_type = ContentType.objects.create(app_label="accounts", model="profile")
        member_permission = Permission.objects.create(content_type=profile_type, codename="view_profile", name="Member permission")
        user_type = ContentType.objects.get(app_label="auth", model="user")
        for model_type, object_id in ((profile_type, 1), (user_type, members[0].pk), (user_type, admins[0].pk)):
            LogEntry.objects.create(user_id=admins[0].pk, content_type=model_type, object_id=str(object_id), object_repr="test-only", action_flag=1)

        purge = import_module("accounts.migrations.0005_purge_legacy_members").purge_legacy_members
        try:
            for _ in range(2):
                with connection.schema_editor() as editor:
                    purge(apps, editor)
            self.assertEqual(list(User.objects.order_by("pk").values()), original_admins)
            self.assertEqual(list(Session.objects.values_list("session_key", flat=True)), ["admin-session"])
            self.assertNotIn("accounts_profile", connection.introspection.table_names())
            self.assertFalse(ContentType.objects.filter(app_label="accounts").exists())
            self.assertFalse(Permission.objects.filter(pk=member_permission.pk).exists())
            self.assertEqual(list(LogEntry.objects.values_list("object_id", flat=True)), [str(admins[0].pk)])
        finally:
            if "accounts_profile" in connection.introspection.table_names():
                with connection.schema_editor() as editor:
                    editor.delete_model(Profile)
