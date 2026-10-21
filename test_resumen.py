import sys, os
sys.path.insert(0, r"C:\Users\Usuario\Desktop\Proyecto Computadoras - Prestamos")
os.chdir(r"C:\Users\Usuario\Desktop\Proyecto Computadoras - Prestamos")
from app import create_app, db
from app.models import Prestamo, get_estado_resumen
from datetime import date
app = create_app()
with app.app_context():
    today = date(2026, 10, 21)
    activos = Prestamo.query.filter(Prestamo.fecha_prestamo == today, Prestamo.estado == 'activo').all()
    print('Activos hoy:', len(activos))
    for a in activos:
        print('  ID', a.id, 'cant', a.cantidad, 'fecha', a.fecha_prestamo)
    resumen = get_estado_resumen(today)
    print('Resumen:', resumen)
