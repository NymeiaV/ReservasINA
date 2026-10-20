#!/usr/bin/env python3
"""
Update computer states script - fixed version.
Instead of updating per-computer states (table removed), this script
prints current availability statistics.
"""

from app import create_app, db
from app.models import get_estado_resumen, calcular_minimo_disponible_fecha_hora, TOTAL_COMPUTADORAS, MAQUINAS_MANTENIMIENTO
from datetime import datetime, timedelta

def main():
    app = create_app()
    with app.app_context():
        now = datetime.now()
        today = now.date()
        # Current availability (only activo loans affect en uso)
        res = get_estado_resumen(today)
        disponibles = res['disponibles']
        en_uso = res['en_uso']
        total = res['total']
        # Minimum availability in the next hour (from now to now+1h)
        hora_inicio = now.time()
        hora_fin = (now + timedelta(hours=1)).time()
        # Note: calcular_minimo_disponible_fecha_hora expects date and time objects
        min_disponible = calcular_minimo_disponible_fecha_hora(today, hora_inicio, hora_fin)
        # Maintenance list
        mantencion = MAQUINAS_MANTENIMIENTO
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Computer Availability Report")
        print(f"  Total computers: {total}")
        print(f"  Available (disponible): {disponibles}")
        print(f"  In use (en uso): {en_uso}")
        print(f"  Minimum available in next hour: {min_disponible}")
        print(f"  Maintenance computers: {mantencion}")

if __name__ == '__main__':
    main()