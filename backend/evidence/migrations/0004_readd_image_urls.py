from django.db import migrations, models


def add_image_urls_if_missing(apps, schema_editor):
    Evidence = apps.get_model("evidence", "Evidence")
    table = Evidence._meta.db_table

    cursor = schema_editor.connection.cursor()
    existing_cols = {
        c.name
        for c in schema_editor.connection.introspection.get_table_description(cursor, table)
    }
    if "image_urls" in existing_cols:
        return

    field = models.JSONField(default=list, blank=True)
    field.set_attributes_from_name("image_urls")
    schema_editor.add_field(Evidence, field)


def drop_image_urls_if_exists(apps, schema_editor):
    Evidence = apps.get_model("evidence", "Evidence")
    table = Evidence._meta.db_table

    cursor = schema_editor.connection.cursor()
    existing_cols = {
        c.name
        for c in schema_editor.connection.introspection.get_table_description(cursor, table)
    }
    if "image_urls" not in existing_cols:
        return

    field = Evidence._meta.get_field("image_urls")
    schema_editor.remove_field(Evidence, field)


class Migration(migrations.Migration):
    dependencies = [
        ("evidence", "0003_remove_evidence_image_urls_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_image_urls_if_missing, reverse_code=drop_image_urls_if_exists),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="evidence",
                    name="image_urls",
                    field=models.JSONField(default=list, blank=True),
                )
            ],
        )
    ]