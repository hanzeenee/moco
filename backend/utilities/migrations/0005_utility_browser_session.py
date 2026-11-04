from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("utilities", "0004_account_number_only"),
    ]

    operations = [
        migrations.CreateModel(
            name="UtilityBrowserSession",
            fields=[
                ("token_hash", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="browser_sessions", to="utilities.utilityaccessaccount")),
            ],
        ),
    ]
