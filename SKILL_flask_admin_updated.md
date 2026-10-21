---
name: flask-equipment-admin-panel
category: software-development
description: 'Add an admin page to a Flask loan system to manage machines, users, and dynamic total count (via instance/config_total.txt).'
---

# Flask Equipment Admin Panel

## Trigger
When adding `/admin` to a Flask loan app that manages `TOTAL_COMPUTADORAS`, `MAQUINAS_MANTENIMIENTO`, and `usuarios` via an `instance/config_total.txt` file.

## Key Points
- Create `app/admin_route.py` with blueprint `admin` (NOT `main`).
- Read `instance/config_total.txt` at startup in `models.py`; write it from `/admin` POST (`actualizar_total`).
- Ensure `base.html` links to `url_for('admin.admin')`.
- Template `admin.html` uses forms with `accion` hidden fields: `actualizar_total`, `agregar_usuario`, `eliminar_usuario`.
- After changing total, RESTART the Flask process (Python imports `models.py` once; the file is read at import time, not per-request).
- Add `observaciones` column to `prestamos` and save it in `routes.py` `devolver_prestamo()` and `entregar()`.

## Pitfalls
- `Blueprint('main', ...)` conflicts with existing `main` blueprint; use `bp = Blueprint('admin', __name__, url_prefix='')`.
- `models.py` must use `os.path.dirname(os.path.dirname(__file__))` correctly to find `instance/` from inside `app/`.
- If `instance/config_total.txt` is missing when `run.py` starts, `models.py` falls back to default (28). Create the file before starting.
- Do NOT rely solely on `config_total.txt` without a restart; Python reads it once at module import.
- `historial.html` must include collapsible `observaciones` with `data-bs-toggle="collapse"` and `data-bs-target`.

## Verification
- `/admin` loads with sections for machines (total + maintenance) and users (add/list/delete).
- Changing total and clicking save writes `instance/config_total.txt`.
- After server restart, `index.html` shows updated `estado_resumen.total`.
- `observaciones` appears in `devolver_prestamo.html` form and `historial.html` collapsible.
