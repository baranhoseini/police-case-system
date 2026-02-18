from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("evidence", "0003_remove_evidence_image_urls_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="evidence",
            name="image_urls",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
