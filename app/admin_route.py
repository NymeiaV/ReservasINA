from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Usuario, Prestamo, TOTAL_COMPUTADORAS, get_estado_resumen, MAQUINAS_MANTENIMIENTO
from datetime import datetime, date, time, timedelta
import json

bp = Blueprint('admin', __name__, url_prefix='')

# Rutas existentes: index, prestamos, registrar_prestamo, devolver_prestamo, entregar_prestamo, eliminar_prestamo, api_estado_resumen, api_verificar_disponibilidad, historial

# Nueva ruta admin
@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    from app import create_app
    import os
    # Releer configuración dinámica antes de mostrar (para reflejar cambios recientes)
    from app.models import leer_config_dinamica
    leer_config_dinamica()
    
    # Leer configuración actual
    total_actual = TOTAL_COMPUTADORAS
    mantenimientos = MAQUINAS_MANTENIMIENTO
    mantenimiento_str = ','.join(str(x) for x in mantenimientos)
    usuarios = Usuario.query.order_by(Usuario.apellido, Usuario.nombre).all()

    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == 'actualizar_total':
            try:
                nuevo_total = int(request.form.get('total_computadoras', total_actual))
                manten_str = request.form.get('maquinas_mantenimiento', '').strip()
                manten_list = [int(x.strip()) for x in manten_str.split(',') if x.strip().isdigit()]
                # Escribir al archivo models.py temporalmente como archivo de config
                # Pero mejor: actualizar variables del módulo (en memoria) y escribir archivo externo
                # Por simplicidad, actualizamos el archivo externo config_total.txt
                config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'config_total.txt')
                # Asegurar que instance/ existe
                instance_dir = os.path.dirname(config_path)
                if not os.path.exists(instance_dir):
                    os.makedirs(instance_dir, exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(f"{nuevo_total}\n")
                    for m in manten_list:
                        f.write(f"{m}\n")
                flash(f'Total actualizado a {nuevo_total}. Mantenimiento: {manten_list}', 'success')
            except Exception as e:
                flash(f'Error actualizando total: {e}', 'error')
        elif accion == 'agregar_usuario':
            apellido = request.form.get('apellido', '').strip()
            nombre = request.form.get('nombre', '').strip()
            if apellido and nombre:
                nuevo = Usuario(apellido=apellido, nombre=nombre)
                db.session.add(nuevo)
                db.session.commit()
                flash(f'Usuario {nombre} {apellido} agregado.', 'success')
            else:
                flash('Apellido y nombre son obligatorios.', 'error')
        elif accion == 'eliminar_usuario':
            usuario_id = request.form.get('usuario_id', type=int)
            if usuario_id:
                usuario = Usuario.query.get_or_404(usuario_id)
                db.session.delete(usuario)
                db.session.commit()
                flash(f'Usuario {usuario.apellido}, {usuario.nombre} eliminado.', 'success')
        return redirect(url_for('admin.admin'))

    return render_template('admin.html',
                         total_computadoras=total_actual,
                         mantenimiento_str=mantenimiento_str,
                         usuarios=usuarios)
