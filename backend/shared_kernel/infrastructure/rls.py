"""Migration operation that puts a table under forced, fail-closed row-level security."""

from typing import Any

from django.db.migrations.operations.base import Operation

ACTOR = "nullif(current_setting('ascua.actor_id', true), '')::uuid"


class EnableRLS(Operation):
    reversible = True

    def __init__(self, model_name: str, owner_column: str = "owner_id") -> None:
        self.model_name = model_name
        self.owner_column = owner_column

    def state_forwards(self, app_label: str, state: Any) -> None:
        pass

    def _table(self, app_label: str, schema_editor: Any, state: Any) -> str:
        model = state.apps.get_model(app_label, self.model_name)
        return str(schema_editor.quote_name(model._meta.db_table))

    def database_forwards(
        self, app_label: str, schema_editor: Any, from_state: Any, to_state: Any
    ) -> None:
        table = self._table(app_label, schema_editor, to_state)
        column = schema_editor.quote_name(self.owner_column)
        check = f"{column} = {ACTOR}"
        schema_editor.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        schema_editor.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        schema_editor.execute(
            f"CREATE POLICY tenant_isolation ON {table} USING ({check}) WITH CHECK ({check})"
        )

    def database_backwards(
        self, app_label: str, schema_editor: Any, from_state: Any, to_state: Any
    ) -> None:
        table = self._table(app_label, schema_editor, from_state)
        schema_editor.execute(f"DROP POLICY tenant_isolation ON {table}")
        schema_editor.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        schema_editor.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    def describe(self) -> str:
        return f"Enable forced row-level security on {self.model_name}"
