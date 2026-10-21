# Verificación antes de arrancar en el server del cole

# 1. Verificar que el puerto esté libre (ejemplo con 5001)
ss -tuln | grep 5001
# Si no devuelve nada -> libre

# 2. Verificar que app.db existe
ls -la instance/app.db

# 3. Probar la app en ese puerto sin afectar nada
source venv/bin/activate
python -c "
from app import create_app
app = create_app()
print('App carga OK, DB:', app.config.get('SQLALCHEMY_DATABASE_URI'))
"

# 4. Levantar en puerto alternativo (ej. 5001) solo para probar
# (cambiá port=5001 en run.py temporalmente)
# Luego curl: curl -s http://localhost:5001/ | head -n 5

# 5. Si todo responde -> está seguro para usar
# Si algo falla -> no afecta al resto del server
