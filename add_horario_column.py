import os
import sys

# Ensure we can import from the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Check if column exists
    result = db.session.execute(text("PRAGMA table_info(prestamos)"))
    columns = [row[1] for row in result]
    print('Current columns:', columns)
    if 'horario_devolucion' not in columns:
        db.session.execute(text('ALTER TABLE prestamos ADD COLUMN horario_devolucion TIME'))
        db.session.commit()
        print('Added column horario_devolucion')
    else:
        print('Column horario_devolucion already exists')