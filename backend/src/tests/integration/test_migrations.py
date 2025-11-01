import pytest
from alembic import command
from alembic.config import Config
from pathlib import Path


@pytest.mark.integration
def test_migrations_run_successfully(tmp_path: Path, skip_if_no_postgres):
    """Применяет Alembic миграции только если доступен PostgreSQL (иначе skip)."""
    config = Config("backend/src/db/migrations/alembic.ini")
    command.upgrade(config, "head")
    command.downgrade(config, "base")
