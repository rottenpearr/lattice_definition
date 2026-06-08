import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

# Railway (и другие PaaS) выдают DATABASE_URL — парсим его если есть
_db_url = os.getenv("DATABASE_URL", "")
if _db_url:
    _p = urlparse(_db_url)
    db_config = {
        'host':     _p.hostname,
        'port':     _p.port or 5432,
        'user':     _p.username,
        'password': _p.password,
        'dbname':   _p.path.lstrip('/'),
    }
else:
    db_config = {
        'host':     os.getenv('DB_HOST', 'localhost'),
        'port':     int(os.getenv('DB_PORT', '5432')),
        'user':     os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'dbname':   os.getenv('DB_NAME', 'crystal_lattice_db'),
    }
