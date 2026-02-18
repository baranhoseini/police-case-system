from django.core.management.base import BaseCommand
from rbac.models import Role

DEFAULT_ROLES = [
    ("Admin", "Full access"),
    ("Officer", "Officer access"),
    ("Detective", "Detective access"),
    ("Cadet", "Cadet access"),
    ("Supervisor", "Supervisor access"),
    ("Chief", "Chief access"),

    # Missing roles used in endpoints
    ("Patrol", "Patrol officer access"),
    ("Captain", "Captain access"),
    ("Judge", "Judge access"),

    # Spelling variants currently used in code
    ("Sergent", "Sergeant access"),
    ("Sergeant", "Sergeant access"),
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
