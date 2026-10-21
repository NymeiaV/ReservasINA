from app import db
from datetime import datetime, timedelta
import os

# Leer configuración dinámica de total y mantenimiento
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'config_total.txt')
TOTAL_COMPUTADORAS = 28
MAQUINAS_MANTENIMIENTO = [10, 26]

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        lines = f.read().strip().split('\n')
        if lines and lines[0].strip().isdigit():
            TOTAL_COMPUTADORAS = int(lines[0].strip())
        manten = [int(x.strip()) for x in lines[1:] if x.strip().isdigit()]
        if manten:
            MAQUINAS_MANTENIMIENTO = manten
except Exception:
    pass

def leer_config_dinamica():
    global TOTAL_COMPUTADORAS, MAQUINAS_MANTENIMIENTO
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
            if lines and lines[0].strip().isdigit():
                TOTAL_COMPUTADORAS = int(lines[0].strip())
            manten = [int(x.strip()) for x in lines[1:] if x.strip().isdigit()]
            if manten:
                MAQUINAS_MANTENIMIENTO = manten
    except Exception:
        pass

# Las variables TOTAL_COMPUTADORAS y MAQUINAS_MANTENIMIENTO se definen arriba (líneas 7-8) y se actualizan dinámicamente

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apellido = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.apellido}, {self.nombre}>'
    
    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    prestador_id = db.Column(db.Integer, nullable=True)  # No foreign key, just integer
    fecha_prestamo = db.Column(db.Date, nullable=False)
    hora_retiro = db.Column(db.Time, nullable=False)
    hora_devolucion_esperada = db.Column(db.Time, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    hora_devolucion_final = db.Column(db.DateTime, nullable=True)
    horario_devolucion = db.Column(db.Time, nullable=True)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    observaciones = db.Column(db.Text, nullable=True)  # Notas al devolver
    estado = db.Column(db.String(20), nullable=False, default='pendiente_entrega')  # pendiente_entrega, activo, devuelto
    
    # Relationships
    usuario = db.relationship('Usuario', backref='prestamos')
    
    def __repr__(self):
        return f'<Prestamo {self.id}: Usuario {self.usuario_id}, {self.fecha_prestamo} {self.hora_retiro}-{self.hora_devolucion_esperada}, cant={self.cantidad}, est={self.estado}>'
    
    @property
    def devuelto_total(self):
        return self.estado == 'devuelto'
    
    @property
    def cantidad_devuelta(self):
        if self.estado == 'devuelto':
            return self.cantidad
        elif self.estado == 'activo':
            return 0
        return 0
    
    @property
    def cantidad_pendiente(self):
        if self.estado == 'activo':
            return self.cantidad
        return 0

# Funciones helper para calcular disponibilidad

def get_estado_resumen(fecha=None):
    leer_config_dinamica()
    """Retorna dict con disponibles y en_uso para la vista de inicio (solo préstamos activos)"""
    if fecha is None:
        fecha = datetime.now().date()
    
    # Solo préstamos ACTIVOS (entrega confirmada) afectan disponibilidad actual
    prestamos_activos = Prestamo.query.filter(
        Prestamo.fecha_prestamo == fecha,
        Prestamo.estado == 'activo'
    ).all()
    
    en_uso = sum(p.cantidad for p in prestamos_activos)
    disponibles = max(0, TOTAL_COMPUTADORAS - sum(p.cantidad for p in prestamos_activos))
    
    return {
        'disponibles': disponibles,
        'en_uso': sum(p.cantidad for p in prestamos_activos),
        'total': TOTAL_COMPUTADORAS
    }


def calcular_minimo_disponible_fecha_hora(fecha, hora_inicio, hora_fin):
    """
    Calcula el mínimo de máquinas disponibles en cualquier sub-franja
    dentro del intervalo [hora_inicio, hora_fin] para una fecha dada.
    
    Considera préstamos 'activo' y 'pendiente_entrega' que se solapen.
    Retorna el mínimo de máquinas disponibles en cualquier sub-franja.
    """
    # Buscar préstamos que se solapen con el intervalo solicitado
    # (activo + pendiente_entrega que se solapen en horario)
    prestamos_solapados = Prestamo.query.filter(
        Prestamo.fecha_prestamo == fecha,
        Prestamo.estado.in_(['activo', 'pendiente_entrega']),
        Prestamo.hora_retiro < hora_fin,
        Prestamo.hora_devolucion_esperada > hora_inicio
    ).all()
    
    if not prestamos_solapados:
        return TOTAL_COMPUTADORAS
    
    # Crear puntos de corte: inicio/fin del intervalo + inicios/fines de préstamos solapados
    puntos_corte = {hora_inicio, hora_fin}
    for p in prestamos_solapados:
        if p.hora_retiro > hora_inicio and p.hora_retiro < hora_fin:
            puntos_corte.add(p.hora_retiro)
        if p.hora_devolucion_esperada > hora_inicio and p.hora_devolucion_esperada < hora_fin:
            puntos_corte.add(p.hora_devolucion_esperada)
    
    # Ordenar puntos de corte
    puntos_ordenados = sorted(puntos_corte)
    
    # Evaluar cada sub-franja
    minimo_disponibles = TOTAL_COMPUTADORAS
    
    for i in range(len(puntos_ordenados) - 1):
        inicio_sub = puntos_ordenados[i]
        fin_sub = puntos_ordenados[i + 1]
        
        # Tiempo medio de la sub-franja para evaluar
        # Usar la fecha del préstamo, no datetime.today()
        dt_inicio = datetime.combine(fecha, inicio_sub)
        dt_fin = datetime.combine(fecha, fin_sub)
        medio = dt_inicio + (dt_fin - dt_inicio) / 2
        tiempo_medio = medio.time()
        
        # Calcular máquinas en uso en este momento
        en_uso = 0
        for p in prestamos_solapados:
            if p.estado == 'activo':
                loan_start = datetime.combine(fecha, p.hora_retiro)
                loan_end = datetime.combine(fecha, p.hora_devolucion_esperada)
                t_medio = datetime.combine(fecha, tiempo_medio)
                if loan_start <= t_medio < loan_end:
                    en_uso += p.cantidad
            elif p.estado == 'pendiente_entrega':
                # pendiente_entrega: cuenta como comprometido en todo su horario
                if p.hora_retiro <= tiempo_medio < p.hora_devolucion_esperada:
                    en_uso += p.cantidad
        
        disponibles = TOTAL_COMPUTADORAS - en_uso
        minimo_disponibles = min(minimo_disponibles, disponibles)
        
        # Early exit: si ya es 0, no puede empeorar
        if minimo_disponibles == 0:
            break
    
    return minimo_disponibles


def hay_disponibilidad_para_cantidad(fecha, hora_inicio, hora_fin, cantidad):
    """
    Verifica si hay disponibilidad para 'cantidad' máquinas
    durante todo el intervalo [hora_inicio, hora_fin].
    """
    minimo = calcular_minimo_disponible_fecha_hora(fecha, hora_inicio, hora_fin)
    return minimo >= cantidad