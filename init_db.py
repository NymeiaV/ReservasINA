#!/usr/bin/env python3
"""
Script to initialize the database with sample data.
Run with: python init_db.py
"""

from app import create_app, db
from app.models import Computadora, Usuario, Prestador
from datetime import date

def init_db():
    """Initialize the database with sample data."""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created.")
        
        # Check if data already exists
        if Computadora.query.first():
            print("Database already contains data. Skipping initialization.")
            return
        
        # Add 30 computers
        print("Adding 30 computers...")
        for i in range(1, 31):
            comp = Computadora(id=i, estado='disponible')
            db.session.add(comp)
        
        # Add 3 prestadores
        print("Adding prestadores...")
        prestadores_nombres = ['Adrian', 'Vanesa', 'Ariel']
        for nombre in prestadores_nombres:
            prestador = Prestador(nombre=nombre)
            db.session.add(prestador)
        
        # Add 7 sample professors (usuarios)
        print("Adding sample usuarios...")
        usuarios_data = [
            ('García', 'María'),
            ('López', 'Juan'),
            ('Pérez', 'Ana'),
            ('Sánchez', 'Carlos'),
            ('Martínez', 'Elena'),
            ('Rodríguez', 'Miguel'),
            ('Fernández', 'Laura')
        ]
        for apellido, nombre in usuarios_data:
            usuario = Usuario(apellido=apellido, nombre=nombre)
            db.session.add(usuario)
        
        # Commit all changes
        db.session.commit()
        print("Database initialized successfully!")
        print(f"- {Computadora.query.count()} computers added")
        print(f"- {Prestador.query.count()} prestadores added")
        print(f"- {Usuario.query.count()} usuarios added")

if __name__ == '__main__':
    init_db()