# heritages

The project targets Django 5.2.18 with Python 3.10–3.12. Keep the existing
production environment until the upgrade has been tested in a separate one.

```sh
python3.10 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Install the custom `partial-date` package separately:
`.venv/bin/python -m pip install /path/to/partial_date-0.1-py3-none-any.whl`.
The path in `partial_date_requirement.txt` is specific to the original server.

Before upgrading the remote installation:

1. Preserve its app migration files; app migrations are excluded from Git.
2. Check `manage.py showmigrations easyaudit`. The verified starting point is
   easy-audit 1.3.3 with migrations 0001–0016 applied and migration 0004 using
   `AlterIndexTogether`.
3. Deploy `heritages/audit_migrations/` and the `MIGRATION_MODULES` setting.
   This restores the original audit migration 0004 and uses upstream files for
   all other migrations, avoiding duplicate index state in easy-audit 1.3.9.
4. Test against a remote SQLite backup in the new environment. Run
   `manage.py check`, `manage.py makemigrations --check --dry-run`,
   `manage.py migrate --plan`, and `manage.py migrate`.
5. For production deployment, stop application writes, take a fresh database
   backup, apply migrations with the new environment, and switch the application
   to that environment. No `--fake` is needed for the verified migration path.

Run tests with `manage.py test --nomigrations`; migration verification is
separate because this option creates test tables directly from the models.
