"""
Script to split math_checker.py into a routers/math_checker/ package.
We will separate:
1. schemas.py (All Pydantic models)
2. services.py (Helper functions without @router)
3. routes_xxx.py (Router endpoints)
"""
import os

with open("routers/math_checker.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

os.makedirs("routers/math_checker", exist_ok=True)

# We will read line by line and chunk them into entities.
chunks = []
current_chunk = []
current_type = "imports"  # imports, schema, service, route
in_class = False
in_func = False


def flush_chunk(ctype):
    global current_chunk
    if current_chunk:
        chunks.append({"type": ctype, "lines": current_chunk})
        current_chunk = []


for i, line in enumerate(lines):
    if i == 0 or current_type == "imports":
        # collect imports up to line 17 or so (before router = APIRouter)
        if line.startswith("router = APIRouter"):
            flush_chunk("imports")
            current_chunk.append(line)
            flush_chunk("router_init")
            current_type = "other"
            continue
        else:
            current_chunk.append(line)
            continue

    # Once past imports:
    if line.startswith("class ") and "(BaseModel)" in line:
        flush_chunk(current_type)
        current_type = "schema"
        current_chunk.append(line)
    elif line.startswith("@router."):
        flush_chunk(current_type)
        current_type = "route"
        current_chunk.append(line)
    elif line.startswith("def ") or line.startswith("async def "):
        if current_type != "route":  # Because @router decorators precede def
            flush_chunk(current_type)
            current_type = "service"
        current_chunk.append(line)
    else:
        # continuation of current chunk
        # if it's empty string or comments between chunks, it goes to the current one
        current_chunk.append(line)

flush_chunk(current_type)

imports = "".join(chunks[0]["lines"]).replace("router = APIRouter(prefix=\"/math\", tags=[\"math\"])\n", "")

schemas_lines = []
for c in chunks:
    if c["type"] == "schema":
        schemas_lines.extend(c["lines"])

services_lines = []
for c in chunks:
    if c["type"] == "service":
        services_lines.extend(c["lines"])

routes_lines = []
for c in chunks:
    if c["type"] == "route":
        routes_lines.extend(c["lines"])

# Write schemas.py
with open("routers/math_checker/schemas.py", "w", encoding="utf-8") as f:
    f.write(imports + "\n" + "".join(schemas_lines))
print("Created schemas.py")

# Write services.py
with open("routers/math_checker/services.py", "w", encoding="utf-8") as f:
    f.write(imports + "\nfrom .schemas import *\n\n" + "".join(services_lines))
print("Created services.py")

# Write routes.py
route_header = imports + """
from fastapi import APIRouter
from .schemas import *
from .services import *

router = APIRouter(prefix="/math", tags=["math"])
"""
with open("routers/math_checker/routes.py", "w", encoding="utf-8") as f:
    f.write(route_header + "\n" + "".join(routes_lines))
print("Created routes.py")

# Write __init__.py
init_header = """
from .routes import router

__all__ = ["router"]
"""
with open("routers/math_checker/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_header)
print("Created __init__.py")

print("Backup created, now checking.")
