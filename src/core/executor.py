from django.db.migrations.executor import MigrationExecutor as OriginMigrationExecutor
from django.db.migrations.loader import MigrationLoader
from .recorder import MigrationRecorder

from django.db.migrations.executor import InvalidMigrationPlan


class MigrationExecutor(OriginMigrationExecutor):
    """
    End-to-end migration execution - load migrations and run them up or down
    to a specified set of targets.
    """

    def __init__(self, connection, progress_callback=None):
        self.connection = connection
        self.loader = MigrationLoader(self.connection)
        self.recorder = MigrationRecorder(self.connection)
        self.progress_callback = progress_callback

    def migrate(self, targets, plan=None, state=None, fake=False, fake_initial=False):
        """
        Migrate the database up to the given targets.

        Django first needs to create all project states before a migration is
        (un)applied and in a second step run all the database operations.
        """
        # The django_migrations table must be present to record applied
        # migrations.

        self.recorder.ensure_schema()

        if plan is None:
            plan = self.migration_plan(targets)
        # Create the forwards plan Django would follow on an empty database
        full_plan = self.migration_plan(
            self.loader.graph.leaf_nodes(), clean_start=True
        )

        all_forwards = all(not backwards for mig, backwards in plan)
        all_backwards = all(backwards for mig, backwards in plan)

        if not plan:
            if state is None:
                # The resulting state should include applied migrations.
                state = self._create_project_state(with_applied_migrations=True)
        elif all_forwards == all_backwards:
            # This should only happen if there's a mixed plan
            raise InvalidMigrationPlan(
                "Migration plans with both forwards and backwards migrations "
                "are not supported. Please split your migration process into "
                "separate plans of only forwards OR backwards migrations.",
                plan,
            )
        elif all_forwards:
            if state is None:
                # The resulting state should still include applied migrations.
                state = self._create_project_state(with_applied_migrations=True)
            state = self._migrate_all_forwards(
                state, plan, full_plan, fake=fake, fake_initial=fake_initial
            )
        else:
            # No need to check for `elif all_backwards` here, as that condition
            # would always evaluate to true.
            state = self._migrate_all_backwards(plan, full_plan, fake=fake)

        self.check_replacements()

        return state
