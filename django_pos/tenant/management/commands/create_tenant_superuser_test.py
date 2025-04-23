from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperuserCommand
from django.core.management.base import CommandError
from django_tenants.utils import get_tenant_model, tenant_context
from django.contrib.auth import get_user_model


class Command(CreateSuperuserCommand):
    help = "Create a superuser for a specific tenant"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--schema', type=str, help='Tenant schema name')

    def handle(self, *args, **options):
        schema = options.get('schema')
        if not schema:
            raise CommandError("You must specify a tenant schema with --schema")

        # Get the tenant
        TenantModel = get_tenant_model()
        try:
            tenant = TenantModel.objects.get(schema_name=schema)
        except TenantModel.DoesNotExist:
            raise CommandError(f"Tenant with schema '{schema}' does not exist")

        with tenant_context(tenant):
            self.UserModel = get_user_model()

            # Collect user input
            username = options.get("username") or input("Username: ")
            email = options.get("email") or input("Email address: ")
            password = options.get("password")
            if not password:
                from django.contrib.auth.password_validation import validate_password
                from django.core.exceptions import ValidationError
                from getpass import getpass

                while True:
                    password = getpass("Password: ")
                    password2 = getpass("Password (again): ")
                    if password != password2:
                        print("Error: Passwords do not match.")
                        continue
                    try:
                        validate_password(password)
                        break
                    except ValidationError as e:
                        print("Error:", e)

            # Create user and assign tenant
            self.UserModel.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                tenant=tenant
            )

            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created for tenant '{schema}'"))
