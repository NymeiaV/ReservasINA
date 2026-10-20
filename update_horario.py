from app import create_app, db
from app.models import Prestamo

app = create_app()
with app.app_context():
    # Update existing loans to set horario_devolucion from hora_devolucion_final where it's NULL
    loans = Prestamo.query.filter(Prestamo.hora_devolucion_final.isnot(None), Prestamo.horario_devolucion.is_(None)).all()
    print(f"Found {len(loans)} loans to update")
    for loan in loans:
        if loan.hora_devolucion_final:
            loan.horario_devolucion = loan.hora_devolucion_final.time()
            print(f"Updated loan {loan.id}: horario_devolucion set to {loan.horario_devolucion}")
    db.session.commit()
    print("Update complete")