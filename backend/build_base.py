import os
import sys

base_dir = r"c:\Users\thispc\Downloads\NextRoute\backend"

files = {}

files["requirements.txt"] = """
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
alembic==1.13.0
psycopg2-binary==2.9.9
aiosqlite==0.20.0
pydantic==2.9.0
pydantic-settings==2.5.0
networkx==3.3
redis==5.1.0
geopy==2.4.0
python-dotenv==1.0.1
httpx==0.27.0
"""

files[".env.example"] = """
DATABASE_URL=sqlite+aiosqlite:///./nextroute.db
REDIS_URL=redis://localhost:6379
GRAPH_DATA_DIR=./graph_data
NEARBY_RADIUS_KM=30
MAX_TRANSFERS=3
MIN_TRANSFER_BUFFER_MINS=20
K_SHORTEST_PATHS=50
SEARCH_RESULT_LIMIT=10
"""

files["alembic.ini"] = """
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = sqlite+aiosqlite:///./nextroute.db

[post_write_hooks]
[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers =
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

files["app/__init__.py"] = ""
files["app/domain/__init__.py"] = ""
files["app/domain/entities/__init__.py"] = ""
files["app/domain/value_objects/__init__.py"] = ""
files["app/domain/interfaces/__init__.py"] = ""
files["app/application/__init__.py"] = ""
files["app/application/use_cases/__init__.py"] = ""
files["app/application/dto/__init__.py"] = ""
files["app/infrastructure/__init__.py"] = ""
files["app/infrastructure/database/__init__.py"] = ""
files["app/infrastructure/repositories/__init__.py"] = ""
files["app/infrastructure/graph/__init__.py"] = ""
files["app/infrastructure/providers/__init__.py"] = ""
files["app/presentation/__init__.py"] = ""
files["app/presentation/api/__init__.py"] = ""
files["app/presentation/api/v1/__init__.py"] = ""
files["app/presentation/schemas/__init__.py"] = ""
files["app/engines/__init__.py"] = ""
files["alembic/versions/.gitkeep"] = ""

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n" if content else "")

print("Base structure generated.")
