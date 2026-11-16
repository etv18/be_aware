"""Write frontend/openapi.json (the OpenAPI document of the JSON API). Run it from the project root:

    python scripts/export_openapi.py

It starts the app with the testing settings (in-memory SQLite), so it needs no database and no .env file.
`npm run gen:api` in /frontend runs this and then generates the TypeScript types from the result.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from app.openapi import write_spec  # noqa: E402

target = ROOT / 'frontend' / 'openapi.json'
write_spec(target, create_app('testing'))
print(f'OpenAPI document written to {target}')
