from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("evidence", "0002_evidence_image_urls_evidence_media_urls_and_more"),
    ]

    operations = [
        # NOTE: "media_urls" is not present in current migration state in this branch.
        # Removing it here avoids KeyError during state construction.
    ]
