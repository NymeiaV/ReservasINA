from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Usuario, Prestamo, TOTAL_COMPUTADORAS, get_estado_resumen, MAQUINAS_MANTENIMIENTO
from datetime import datetime, date, time, timedelta
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get today's loans to show below the grid
    today = date.today()
    prestamos_hoy = Prestamo.query.filter(
        Prestamo.fecha_prestamo == today
    ).order_by(Prestamo.hora_retiro).all()
    
    # Get estado resumen for the counters
    estado_resumen = get_estado_resumen(today)
    
    return render_template('index.html', 
                         prestamos_hoy=prestamos_hoy, 
                         today=today,
                         estado_resumen=estado_resumen,
                         maquinas_mantenimiento=MAQUINAS_MANTENIMIENTO)

@bp.route('/prestamos')
def prestamos():
    # Get all loans for the current week (Monday to Friday)
    from datetime import date, timedelta
    today = date.today()
    # Calculate Monday of current week
    days_to_monday = (today.weekday() + 6) % 7  # Monday = 0
    monday = today - timedelta(days=days_to_monday)
    friday = monday + timedelta(days=4)
    
    # Get all loans for this week (Mon-Fri)
    prestamos_semana = Prestamo.query.filter(
        Prestamo.fecha_prestamo >= monday,
        Prestamo.fecha_prestamo <= friday
    ).order_by(Prestamo.fecha_prestamo, Prestamo.hora_retiro).all()
    
    # Group by date
    from collections import defaultdict
    prestamos_por_dia = defaultdict(list)
    for p in prestamos_semana:
        prestamos_por_dia[p.fecha_prestamo].append(p)
    
    # Create sorted list of days with loans
    dias_con_prestamos = []
    current_day = monday
    while current_day <= friday:
        if current_day in prestamos_por_dia:
            dias_con_prestamos.append({
                'fecha': current_day,
                'prestamos': prestamos_por_dia[current_day]
            })
        current_day += timedelta(days=1)
    
    return render_template('prestamos.html', 
                         dias_con_prestamos=dias_con_prestamos, 
                         today=today, 
                         monday=monday, 
                         friday=friday)

@bp.route('/registrar_prestamo', methods=['GET', 'POST'])
def registrar_prestamo():
    if request.method == 'GET':
        # Show form to register a new loan
        usuarios = Usuario.query.order_by(Usuario.apellido, Usuario.nombre).all()
        # prestadores = Prestador.query.order_by(Prestador.nombre).all()
        from app.models import TOTAL_COMPUTADORAS
        return render_template('registrar_prestamo.html', 
                             usuarios=usuarios, 
                             # prestadores=prestadores,
                             total_computadoras=TOTAL_COMPUTADORAS)
    elif request.method == 'POST':
        # Process the loan registration
        try:
            usuario_id = request.form.get('usuario_id')
            # prestador_id = request.form.get('prestador_id')
            fecha_prestamo = request.form.get('fecha_prestamo')
            hora_retiro = request.form.get('hora_retiro')
            hora_devolucion = request.form.get('hora_devolucion')
            cantidad = request.form.get('cantidad', type=int)
        
            # Validation
            if not all([usuario_id, fecha_prestamo, hora_retiro, hora_devolucion]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('main.registrar_prestamo'))
        
            if not cantidad or cantidad <= 0:
                flash('Debe indicar una cantidad de máquinas mayor a 0', 'error')
                return redirect(url_for('main.registrar_prestamo'))
            
            # Validar fecha no pasada
            fecha = datetime.strptime(fecha_prestamo, '%Y-%m-%d').date()
            if fecha < date.today():
                flash('No se pueden crear reservas para fechas pasadas', 'error')
                return redirect(url_for('main.registrar_prestamo'))
            
            # Validar hora_retiro < hora_devolucion (horario 6:00-18:30, no cruza medianoche)
            hora_inicio = datetime.strptime(hora_retiro, '%H:%M').time()
            hora_fin = datetime.strptime(hora_devolucion, '%H:%M').time()
            if hora_inicio >= hora_fin:
                flash('La hora de retiro debe ser anterior a la hora de devolución', 'error')
                return redirect(url_for('main.registrar_prestamo'))
            
            # Validar horario dentro del rango permitido (6:00 - 18:30)
            if hora_inicio < time(6, 0) or hora_fin > time(18, 30):
                flash('El horario debe estar entre 06:00 y 18:30', 'error')
                return redirect(url_for('main.registrar_prestamo'))
            
            # Validar disponibilidad usando lógica por franjas (mínimo disponible en cualquier sub-franja)
            from app.models import hay_disponibilidad_para_cantidad, TOTAL_COMPUTADORAS
            if fecha >= date.today():
                if not hay_disponibilidad_para_cantidad(fecha, hora_inicio, hora_fin, cantidad):
                    # Calcular info para mensaje de error
                    from app.models import calcular_minimo_disponible_fecha_hora
                    minimo = calcular_minimo_disponible_fecha_hora(fecha, hora_inicio, hora_fin)
                    maquinas_comprometidas = TOTAL_COMPUTADORAS - minimo
                    flash(
                        f'No hay suficientes máquinas disponibles para ese horario. '
                        f'Máquinas libres garantizadas en toda la franja: {minimo} '
                        f'(comprometidas en horarios pico: {TOTAL_COMPUTADORAS - minimo}). '
                        f'Reduzca la cantidad a {minimo} o menos, o cambie el horario.',
                        'error'
                    )
                    return redirect(url_for('main.registrar_prestamo'))
            
            # Create the loan record
            nuevo_prestamo = Prestamo(
                usuario_id=usuario_id,
                # prestador_id=prestador_id,
                fecha_prestamo=fecha,
                hora_retiro=hora_inicio,
                hora_devolucion_esperada=hora_fin,
                cantidad=cantidad,
                estado='pendiente_entrega'
            )
            db.session.add(nuevo_prestamo)
            db.session.commit()
            flash(f'Reserva registrada exitosamente para {cantidad} máquina(s). Pendiente de entrega.', 'success')
            return redirect(url_for('main.index'))
    
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el préstamo: {str(e)}', 'error')
            return redirect(url_for('main.registrar_prestamo'))

@bp.route('/devolver_prestamo/<int:prestamo_id>', methods=['GET', 'POST'])
def devolver_prestamo(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    if request.method == 'GET':
        return render_template('devolver_prestamo.html', prestamo=prestamo)
    
    elif request.method == 'POST':
        try:
            devolucion_total = request.form.get('devolucion_total') == 'on'
            cantidad_devuelta = request.form.get('cantidad_devuelta', type=int)
            
            if devolucion_total:
                # Devolver todo
                prestamo.estado = 'devuelto'
                ahora = datetime.now()
                prestamo.hora_devolucion_final = ahora
                prestamo.horario_devolucion = ahora.time()
                flash('Devolución total registrada exitosamente', 'success')
            else:
                # Devolución parcial - usar cantidad_devuelta
                if not cantidad_devuelta or cantidad_devuelta <= 0:
                    flash('Debe indicar una cantidad a devolver', 'error')
                    return redirect(url_for('main.devolver_prestamo', prestamo_id=prestamo_id))
                
                if cantidad_devuelta > prestamo.cantidad:
                    flash('No puede devolver más de lo prestado', 'error')
                    return redirect(url_for('main.devolver_prestamo', prestamo_id=prestamo_id))
                
                # Devolución parcial: reducir la cantidad prestada
                prestamo.cantidad -= cantidad_devuelta
                
                # Si se devolvieron todas, marcar como devuelto
                if prestamo.cantidad == 0:
                    prestamo.estado = 'devuelto'
                    ahora = datetime.now()
                    prestamo.hora_devolucion_final = ahora
                    prestamo.horario_devolucion = ahora.time()
                    flash(f'Devolución parcial de {cantidad_devuelta} máquina(s). Préstamo completado.', 'success')
                else:
                    flash(f'Devolución parcial de {cantidad_devuelta} máquina(s) registrada. Quedan {prestamo.cantidad} pendientes.', 'success')
            
            db.session.commit()
            flash('Devolución registrada exitosamente', 'success')
            return redirect(url_for('main.prestamos'))
    
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la devolución: {str(e)}', 'error')
            return redirect(url_for('main.devolver_prestamo', prestamo_id=prestamo_id))

@bp.route('/entregar/<int:prestamo_id>', methods=['GET', 'POST'])
def entregar_prestamo(prestamo_id):
    """Confirmar entrega de máquinas para un préstamo pendiente_entrega"""
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    if prestamo.estado != 'pendiente_entrega':
        flash('Este préstamo ya no está pendiente de entrega', 'error')
        return redirect(url_for('main.prestamos'))
    
    if request.method == 'GET':
        # En el modelo simplificado, solo confirmamos la entrega sin elegir máquinas específicas
        # Verificamos disponibilidad estimada
        fecha = prestamo.fecha_prestamo
        ahora = datetime.now()
        loan_start = datetime.combine(fecha, prestamo.hora_retiro)
        
        # Verificar si hay disponibilidad real
        estado_resumen = get_estado_resumen(fecha)
        disponibles = estado_resumen['disponibles']
        
        return render_template('entregar.html', 
                             prestamo=prestamo,
                             disponibles=disponibles)
    
    elif request.method == 'POST':
        try:
            # Confirmar entrega - cambiar estado a activo
            prestamo.estado = 'activo'
            db.session.commit()
            flash(f'Entrega confirmada: {prestamo.cantidad} máquina(s) entregadas', 'success')
            return redirect(url_for('main.prestamos'))
    
        except Exception as e:
            db.session.rollback()
            flash(f'Error al confirmar la entrega: {str(e)}', 'error')
            return redirect(url_for('main.entregar_prestamo', prestamo_id=prestamo_id))

@bp.route('/eliminar_prestamo/<int:prestamo_id>', methods=['POST'])
def eliminar_prestamo(prestamo_id):
    """Eliminar un préstamo"""
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    try:
        db.session.delete(prestamo)
        db.session.commit()
        flash('Préstamo eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el préstamo: {str(e)}', 'error')
    
    return redirect(url_for('main.prestamos'))

@bp.route('/api/estado_resumen')
def api_estado_resumen():
    """API endpoint to get current counts for dashboard."""
    from datetime import date
    today = date.today()
    estado = get_estado_resumen(today)
    return jsonify(estado)

@bp.route('/api/verificar_disponibilidad', methods=['POST'])
def api_verificar_disponibilidad():
    """API endpoint to check if there are enough machines available for a given time slot.
    Expects JSON: {fecha: 'YYYY-MM-DD', hora_retiro: 'HH:MM', hora_devolucion: 'HH:MM', cantidad: int}"""
    from datetime import datetime, date, time
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos', 'disponible': False}), 400
    
    fecha_str = data.get('fecha')
    hora_retiro_str = data.get('hora_retiro')
    hora_devolucion_str = data.get('hora_devolucion')
    cantidad = data.get('cantidad')
    if cantidad is not None:
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            cantidad = None
    
    if not all([fecha_str, hora_retiro_str, hora_devolucion_str, cantidad is not None]):
        return jsonify({'error': 'Faltan datos: fecha, hora_retiro, hora_devolucion, cantidad', 'disponible': False}), 400
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_retiro_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_devolucion_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Formato de fecha/hora inválido', 'disponible': False}), 400
    
    # Validaciones básicas
    if fecha < date.today():
        return jsonify({'error': 'No se pueden consultar fechas pasadas', 'disponible': False}), 400
    
    if hora_inicio >= hora_fin:
        return jsonify({'error': 'La hora de retiro debe ser anterior a la de devolución', 'disponible': False}), 400
    
    if hora_inicio < time(6, 0) or hora_fin > time(18, 30):
        return jsonify({'error': 'El horario debe estar entre 06:00 y 18:30', 'disponible': False}), 400
    
    if cantidad <= 0 or cantidad > TOTAL_COMPUTADORAS:
        return jsonify({'error': f'Cantidad inválida (1-{TOTAL_COMPUTADORAS})', 'disponible': False}), 400
    
    # Verificar disponibilidad usando lógica por franjas (mínimo disponible)
    from app.models import hay_disponibilidad_para_cantidad, calcular_minimo_disponible_fecha_hora
    
    if not hay_disponibilidad_para_cantidad(fecha, hora_inicio, hora_fin, cantidad):
        minimo = calcular_minimo_disponible_fecha_hora(fecha, hora_inicio, hora_fin)
        return jsonify({
            'disponible': False,
            'maquinas_disponibles': minimo,
            'maquinas_comprometidas': TOTAL_COMPUTADORAS - minimo,
            'cantidad_solicitada': cantidad,
            'mensaje': f'Solo {minimo} máquinas libres garantizadas en toda la franja (necesita {cantidad})'
        }), 400
    
    # Si hay disponibilidad, calcular info para respuesta
    minimo = calcular_minimo_disponible_fecha_hora(fecha, hora_inicio, hora_fin)
    maquinas_disponibles = minimo
    maquinas_comprometidas = TOTAL_COMPUTADORAS - minimo
    
    return jsonify({
        'disponible': True,
        'maquinas_disponibles': maquinas_disponibles,
        'maquinas_comprometidas': TOTAL_COMPUTADORAS - minimo,
        'cantidad_solicitada': cantidad,
        'mensaje': f'{maquinas_disponibles} máquinas libres garantizadas en toda la franja'
    })

@bp.route('/historial')
def historial():
    """Historial de préstamos devueltos"""
    # Get filter parameters
    profesor_id = request.args.get('profesor_id', type=int)
    # prestador_id = request.args.get('prestador_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    # Base query: loans that are fully returned
    query = Prestamo.query.filter(
        Prestamo.estado == 'devuelto'
    )
    
    # Apply filters
    if profesor_id:
        query = query.filter(Prestamo.usuario_id == profesor_id)
        
    # if prestador_id:
    #     query = query.filter(Prestamo.prestador_id == prestador_id)
        
    if fecha_desde:
        query = query.filter(Prestamo.fecha_prestamo >= fecha_desde)
        
    if fecha_hasta:
        query = query.filter(Prestamo.fecha_prestamo <= fecha_hasta)
    
    # Get results
    prestamos = query.order_by(Prestamo.fecha_creacion.desc()).all()
    
    # Get data for filters
    usuarios = Usuario.query.order_by(Usuario.apellido, Usuario.nombre).all()
    # prestadores = Prestador.query.order_by(Prestador.nombre).all()
    
    # Prepare filters dictionary for template
    filtros = {
        'profesor_id': profesor_id,
        # 'prestador_id': prestador_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }
    
    return render_template('historial.html', 
                         prestamos=prestamos,
                         usuarios=usuarios,
                         # prestadores=prestadores,
                         filtros=filtros)