from django.core.management.base import BaseCommand
from tenant.models import Tenant, Domain  # Adjust imports according to your actual models
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Creates a new tenant with a domain'

    def add_arguments(self, parser):
        parser.add_argument('tenant_name', type=str, help='The name of the tenant')
        parser.add_argument('domain', type=str, help='The domain for the tenant')

    def handle(self, *args, **options):
        tenant_name = options['tenant_name']
        domain_name = options['domain']

        # Check if tenant already exists
        if Tenant.objects.filter(name=tenant_name).exists():
            self.stdout.write(self.style.ERROR(f'Tenant "{tenant_name}" already exists.'))
            return

        # Create new tenant
        tenant = Tenant(name=tenant_name)
        try:
            tenant.full_clean()
            tenant.save()
            self.stdout.write(self.style.SUCCESS(f'Tenant "{tenant_name}" created successfully.'))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Error creating tenant: {e}'))
            return

        # Create domain for the tenant
        domain = Domain(domain=domain_name, tenant=tenant, is_primary=True)
        try:
            domain.full_clean()
            domain.save()
            self.stdout.write(self.style.SUCCESS(f'Domain "{domain_name}" created for tenant "{tenant_name}".'))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Error creating domain: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Tenant and domain setup completed for "{tenant_name}".'))
