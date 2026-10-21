# Subir a PythonAnywhere (pasos simples)

1. Creá cuenta gratuita en pythonanywhere.com
2. Abrí una Bash console en el panel web
3. Subí los archivos: git clone o subir por web (carpeta del proyecto + instance/app.db)
4. Creá entorno virtual: python3 -m venv venv
5. source venv/bin/activate
6. pip install -r requirements.txt
7. Configurá una Web App: elegir Flask, apuntar a run.py, puerto automático
8. PythonAnywhere lee instance/app.db automáticamente con Flask
9. Listo: URL pública tipo usuario.pythonanywhere.com

Nota: en el plan gratuito, la app se duerme si no hay tráfico. Para 4-5 registros/día alcanza.
