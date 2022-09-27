#### To get started, add packages and then run this with the following:
- `poetry add <package>` for packages - dotenv, sqlalchemy, mysqlclient, schedule
- `poetry run python3.9 crypto_api.py`
- I dropped the env files in a .env file for the project to read from in `config.py`


#### Connect to db in container with
1. `mysql -h 127.0.0.1 -P 3306 -u docker -p`
2. `USE crypto;`
3. observe tables with `DESCRIBE crypto.tableName;`

#### Extra notes:
- Issues found in code are written, and had to change order of a command
  in Dockerfile to start app and use poetry correctly for adding pkgs
- For instructions, P&L doesn't make sense as we haven't
  described a scenario of selling, only bidding
- Some code choices were described in the code with more optimal
  suggestions. This includes using Alembic for migrations, Airflow
  DAG for scheduled runs, use a connection pool to maintain
  connections to DB, and more.
