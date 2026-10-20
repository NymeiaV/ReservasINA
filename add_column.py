from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Use raw SQL to add column if it doesn't exist
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE prestamos ADD COLUMN hora_devolucion_final DATETIME'))
            conn.commit()
        print('Column hora_devolucion_final added successfully')
    except Exception as e:
        # Check if it's a duplicate column error (SQLite specific)
        if 'duplicate column name' in str(e) or 'already exists' in str(e):
            print('Column hora_devolucion_final already exists')
        else:
            print('Error:', e)
            raise