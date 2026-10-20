# Repaso completo: subir al Linux del cole (sin gunicorn)

## 1. Qué subir (NO incluir venv/, __pycache__/, flask.log)
- Todo el directorio del proyecto
- Importante: instance/app.db (la base SQLite)

## 2. En el servidor Linux (desde 0)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## 3. Correr (manual, sin gunicorn, sin servicio automático)
python run.py

## 4. Base de datos
- instance/app.db se sube junto con todo
- Se lee automáticamente; no hay que instalar nada aparte
- Se actualiza sola cuando registrás/devolvés

## 5. Si se corta la luz / se apaga
Al entrar al server, repetís paso 2 (activar venv) y paso 3 (python run.py)
No hay servicio automático; es manual.
