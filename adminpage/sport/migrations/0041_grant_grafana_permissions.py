# Generated by Django 3.0.7 on 2020-12-31 08:32
from os import getenv

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('sport', '0040_create_grafana_user'),
    ]
    grafana_user = getenv('GRAFANA_DB_USER')
    db_name = getenv('POSTGRES_DB')

    operations = {
        migrations.RunSQL(
            "grant connect on database "
            f"{db_name} to {grafana_user};",
            reverse_sql=f"drop owned by {grafana_user};"
        ),
        migrations.RunSQL(
            f"grant usage on schema public to {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"grant select on all tables in schema public to {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"grant select on all sequences in schema public "
            f"to {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            'alter default privileges in schema public '
            f'grant select on tables to {grafana_user};',
            reverse_sql=migrations.RunSQL.noop
        ),
        # Revoke extra permissions
        # SELECT CONCAT('REVOKE ALL ON public.', table_name, ' FROM
        # grafana;')
        # FROM information_schema.tables
        # WHERE table_schema = 'public'
        #   AND(table_name like 'auth%'
        #   OR table_name like 'django%');
        migrations.RunSQL(
            f"REVOKE ALL ON public.auth_permission FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.auth_user_user_permissions "
            f"FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.django_migrations FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.django_session FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.auth_group FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.django_content_type FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.auth_user_groups FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.django_admin_log FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.auth_user FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            f"REVOKE ALL ON public.auth_group_permissions "
            f"FROM {grafana_user};",
            reverse_sql=migrations.RunSQL.noop
        ),
        # Allow select on some users
        migrations.RunSQL(
            "grant select (id, first_name, last_name, email) "
            f"on auth_user to {grafana_user};",
            reverse_sql=migrations.RunSQL.noop,
        )
    }
