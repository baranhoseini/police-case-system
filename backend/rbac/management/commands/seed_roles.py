from django.core.management.base import BaseCommand
from rbac.models import Role

# Seed both document-canonical names and legacy/internal aliases.
# Permissions are alias-aware (see rbac/permissions.py) so either set works.
DEFAULT_ROLES = [
    # Document-canonical
    ("Administrator", "System administrator (document role: Administrator)"),
    ("Chief", "Chief of police"),
    ("Captain", "Police captain"),
    ("Sergent", "Police sergeant (document spelling)"),
    ("Detective", "Detective"),
    ("Police Officer", "Police officer"),
    ("Patrol Officer", "Patrol officer"),
    ("Cadet", "Cadet / trainee"),
    ("Complainant", "Complainant"),
    ("Witness", "Witness"),
    ("Suspect", "Suspect"),
    ("Criminal", "Criminal"),
    ("Judge", "Judge"),
    ("Corenary", "Forensic doctor (document spelling)"),
    ("Base user", "Base user (default)"),

    # Legacy/internal aliases used in existing code/tests
    ("Admin", "Legacy alias for Administrator"),
    ("Officer", "Legacy alias for Police Officer"),
    ("Patrol", "Legacy alias for Patrol Officer"),
    ("Sergeant", "Legacy alias for Sergent"),
    ("Coroner", "Legacy alias for Corenary"),
    ("Citizen", "Legacy alias for Base user"),
    ("Supervisor", "Extra role referenced in code/tests"),
]


class Command(BaseCommand):
    help = "Create default roles if they do not exist."

    def handle(self, *args, **options):
        created = 0
        for name, desc in DEFAULT_ROLES:
            _, was_created = Role.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"Seeded roles. Created: {created}"))
