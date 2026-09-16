"""Safe database upgrade helper for WorkFlow.
Run from project root: python scripts/upgrade_database.py
"""
from pathlib import Path
from datetime import datetime
import shutil, subprocess, sys

root = Path(__file__).resolve().parents[1]
db = root / "dev.db"
if db.exists():
    backup_dir = root / "backups"; backup_dir.mkdir(exist_ok=True)
    target = backup_dir / f"dev-before-upgrade-{datetime.now():%Y%m%d-%H%M%S}.db"
    shutil.copy2(db, target)
    print(f"Backup criado: {target}")
result = subprocess.run([sys.executable, "-m", "flask", "--app", "main", "db", "upgrade"], cwd=root)
if result.returncode:
    print("Upgrade falhou. O banco original não foi substituído; use o backup se necessário.")
    raise SystemExit(result.returncode)
print("Upgrade concluído.")
