"""Remove retired visitor membership data while preserving Django administrators."""

from importlib import import_module

from django.conf import settings
from django.db import migrations


def purge_legacy_members(apps, schema_editor):
    alias = schema_editor.connection.alias
    User = apps.get_model("auth", "User")
    Session = apps.get_model("sessions", "Session")
    ContentType = apps.get_model("contenttypes", "ContentType")
    LogEntry = apps.get_model("admin", "LogEntry")

    members = User.objects.using(alias).filter(is_staff=False, is_superuser=False)
    member_ids = list(members.values_list("pk", flat=True))
    admin_ids = set(
        str(pk) for pk in User.objects.using(alias).exclude(
            is_staff=False, is_superuser=False
        ).values_list("pk", flat=True)
    )

    # Keep valid administrator sessions; discard retired member/anonymous sessions.
    store = import_module(settings.SESSION_ENGINE).SessionStore()
    for session in Session.objects.using(alias).all().iterator():
        if str(store.decode(session.session_data).get("_auth_user_id")) not in admin_ids:
            Session.objects.using(alias).filter(pk=session.pk).delete()

    # Remove membership-specific log representations and permissions as well.
    LogEntry.objects.using(alias).filter(content_type__app_label="accounts").delete()
    user_type = ContentType.objects.using(alias).filter(app_label="auth", model="user").first()
    if user_type:
        LogEntry.objects.using(alias).filter(
            content_type_id=user_type.pk, object_id__in=[str(pk) for pk in member_ids]
        ).delete()
    members.delete()
    ContentType.objects.using(alias).filter(app_label="accounts").delete()

    table = "accounts_profile"
    if table in schema_editor.connection.introspection.table_names():
        schema_editor.execute(f"DROP TABLE {schema_editor.quote_name(table)}")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_retire_profile"),
        ("admin", "0003_logentry_add_action_flag_choices"),
        ("sessions", "0001_initial"),
    ]

    # Data removal is intentionally irreversible; recovery uses the deployment backup.
    operations = [migrations.RunPython(purge_legacy_members)]
