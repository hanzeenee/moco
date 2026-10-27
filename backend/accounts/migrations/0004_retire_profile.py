from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_profile_name")]

    operations = [
        # Archive records without leaving a live relation that blocks admin user deletion.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AlterField(
                    model_name="profile",
                    name="user",
                    field=models.BigIntegerField(db_column="user_id", unique=True),
                ),
            ],
            state_operations=[migrations.DeleteModel(name="Profile")],
        ),
    ]
