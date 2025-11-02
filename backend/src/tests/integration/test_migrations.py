import pytest
from alembic import command


@pytest.mark.integration
def test_migrations_run_successfully(alembic_config):
    """
    Применяет все Alembic миграции в CI/backend контейнере.
    Проверяет, что не возникает ошибок.
    """
    command.upgrade(alembic_config, "head")
