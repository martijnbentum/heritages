from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase, override_settings


class AuditMigrationTests(SimpleTestCase):
    @override_settings(MIGRATION_MODULES={'easyaudit': 'heritages.audit_migrations'})
    def test_existing_install_has_one_audit_index(self):
        loader = MigrationLoader(None, replace_migrations=False)
        state = loader.project_state([
            ('easyaudit', '0019_alter_crudevent_changed_fields_and_more'),
        ])
        indexes = state.models['easyaudit', 'crudevent'].options['indexes']
        self.assertEqual(
            [index.name for index in indexes],
            ['easyaudit_c_object__82020b_idx'],
        )
