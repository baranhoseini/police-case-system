# backend/evidence/migrations/0004_readd_image_urls.py
from django.db import migrations, models
import django.contrib.postgres.fields

class Migration(migrations.Migration):

    dependencies = [
    ("evidence", "0003_remove_evidence_image_urls_and_more"),]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE evidence_evidence
                    ADD COLUMN IF NOT EXISTS image_urls jsonb NOT NULL DEFAULT '[]'::jsonb;
                    """,
                    reverse_sql="""
                    ALTER TABLE evidence_evidence
                    DROP COLUMN IF EXISTS image_urls;
                    """,
                )
            ],
            state_operations=[
                migrations.AddField(
                    model_name="evidence",
                    name="image_urls",
                    field=models.JSONField(default=list),
                )
            ],
        )
    ]