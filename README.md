# Sistema de Préstamos de Computadoras

## Descripción
Aplicación web para gestionar el préstamo de 30 computadoras en un entorno educativo. Permite registrar quién toma prestado cada equipo, controlar las fechas y horarios de uso, y gestionar devoluciones parciales o totales.

## Características principales
- Visualización gráfica de las 30 computadoras en formato 2x15
- Codificación por colores: 
  - Verde: Disponible
  - Rojo: Prestado/en uso
  - Amarillo: Solicitado (1 hora antes de la reserva)
- Registro de préstamos con selección de usuario, fecha y horario
- Devoluciones parciales y totales
- Historial de préstamos con filtros
- Interfaz intuitiva y responsive

## Tecnologías utilizadas
- Backend: Python con Flask
- Frontend: HTML5, CSS3, JavaScript vanilla
- Base de datos: SQLite (para desarrollo) / PostgreSQL (para producción)
- Otros: Flask-SQLAlchemy para ORM

## Estructura del proyecto
```
Proyecto Computadoras - Prestamos/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       ├── main.js
│   │       └── prestamos.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── prestamos.html
│       └── historial.html
├── migrations/
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

## Instalación y ejecución
1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Ejecutar la aplicación: `python run.py`
6. Acceder en el navegador: http://localhost:5000

## Próximos pasos
- Implementar autenticación de usuarios
- Generar reportes en PDF/Excel
- Añadir notificaciones por email
- Deploy en servidor de producción