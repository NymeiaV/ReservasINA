from app import create_app, db
app = create_app()
with app.app_context():
    # Get table names
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print('Tables:')
    for t in tables:
        print(t)