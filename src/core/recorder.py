from django.db.migrations.recorder import MigrationRecorder as OriginMigrationRecorder
from django.db import DatabaseError

from django.db.migrations.exceptions import MigrationSchemaMissing


class MigrationRecorder(OriginMigrationRecorder):
    def ensure_schema(self):
        """Ensure the table exists and has the correct schema."""
        # If the table's there, that's fine - we've never changed its schema
        # in the codebase.
        if self.has_table():
            return
        # Make the table
        try:
            with self.connection.schema_editor() as editor:
                # default DB에만 django_migrations 테이블이 생성되도록 합니다.
                db_alias = self.connection.alias
                if db_alias == "default":
                    editor.create_model(self.Migration)
        except DatabaseError as exc:
            raise MigrationSchemaMissing(
                "Unable to create the django_migrations table (%s)" % exc
            )
