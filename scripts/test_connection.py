import sys
from pathlib import Path

# Ensure project root is on sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db import engine


def main() -> None:
    print("Connecting to Postgres using", engine.url)
    with engine.connect() as conn:
        version, dbname = conn.exec_driver_sql("select version(), current_database()").one()
        one = conn.exec_driver_sql("select 1").scalar()
        print("version:", version)
        print("database:", dbname)
        print("select 1:", one)
    print("Connection OK")


if __name__ == "__main__":
    main()
