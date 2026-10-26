from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_alter_comment_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="navlink",
            name="key",
            field=models.CharField(
                choices=[
                    ("home", "홈"),
                    ("ea", "EA 문의"),
                    ("indicator", "인디케이터(지표) 문의"),
                    ("free", "무료 제공"),
                    ("other", "기타 문의"),
                ],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="navlink",
            name="url",
            field=models.URLField(blank=True),
        ),
    ]
