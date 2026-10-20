# Despliegue a servidor Linux (colegio)

## 1. Archivos que DEBES subir al servidor Linux

Copia TODO el directorio del proyecto excepto `venv/`, `__pycache__/`, y `flask.log`:

```
Proyecto Computadoras - Prestamos/
  app/                  (código Flask + templates + static)
  instance/app.db        <-- LA BASE DE DATOS (SQLite, 40 KB)
  migrations/            (historial de cambios DB)
  config.py
  run.py
  requirements.txt
  .env
```

## 2. Cómo cargar la base de datos (lo que preguntaste)

Tu base es SQLite. Es un archivo único: `instance/app.db`.
- **Subilo junto con todo** al servidor Linux.
- Al arrancar la app, Flask la lee automáticamente (está configurada en `config.py` con `SQLALCHEMY_DATABASE_URI`).
- **No necesitas instalar ningún gestor de base aparte** (no MySQL, no PostgreSQL).

Si querés hacer una copia de respaldo antes:
```bash
cp instance/app.db instance/app.db.backup_$(date +%Y%m%d)
```

## 3. En el servidor Linux

```bash
# 1. Clonar o subir archivos (scp / git / usb)
# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Correr (desarrollo rápido)
python run.py

# 4. O correr con gunicorn (recomendado para producción local)
pip install gunicorn
export FLASK_APP=run.py
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

## 4. Notas importantes
- `run.py` usa `debug=True` por defecto — si es para uso real, cambiá a `debug=False`.
- El archivo `instance/app.db` se actualiza automáticamente cuando registrás/devolvés préstamos.
- Si el servidor Linux no tiene `python3`, usá `python` (el `venv` que crees usará el intérprete que invoques).
