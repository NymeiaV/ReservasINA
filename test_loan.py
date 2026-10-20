from app import create_app, db
from app.models import Computadora, Usuario, Prestador, Prestamo, PrestamoDetalle
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Check if there are any existing loans
    loans = Prestamo.query.all()
    print(f"Existing loans: {len(loans)}")
    for l in loans:
        print(f"  Loan {l.id}: user {l.usuario_id}, prestador {l.prestador_id}, date {l.fecha_prestamo}, {l.hora_retiro}-{l.hora_devolucion_esperada}")
        # Count details
        details = PrestamoDetalle.query.filter_by(prestamo_id=l.id).all()
        print(f"    Details: {len(details)} computers")
        for d in details:
            comp = Computadora.query.get(d.computadora_id)
            print(f"      Computer {comp.id}: returned? {d.hora_devolucion_real is not None}")
    
    # Check computer states
    computers = Computadora.query.all()
    print("\nComputer states:")
    for c in computers[:5]:  # first 5
        print(f"  Computer {c.id}: estado={c.estado}, mantenimiento={c.mantenimiento}")
    
    # Let's create a test loan that starts in 10 minutes from now
    # Ensure we have a user and prestador
    user = Usuario.query.first()
    prestador = Prestador.query.first()
    if not user or not prestador:
        print("Error: missing user or prestador")
    else:
        print(f"\nCreating test loan for user {user.id} ({user.nombre_completo}) and prestador {prestador.id} ({prestador.nombre})")
        now = datetime.now()
        start_dt = now + timedelta(minutes=10)  # starts in 10 minutes
        end_dt = start_dt + timedelta(hours=2)  # 2 hour loan
        # Create loan
        loan = Prestamo(
            usuario_id=user.id,
            prestador_id=prestador.id,
            fecha_prestamo=start_dt.date(),
            hora_retiro=start_dt.time(),
            hora_devolucion_esperada=end_dt.time()
        )
        db.session.add(loan)
        db.session.flush()  # get loan.id
        print(f"Created loan ID {loan.id}")
        # Select first 3 available computers (those with estado disponible and not mantenimiento)
        availables = [c for c in computers if c.estado == 'disponible' and not c.mantenimiento]
        selected = availables[:3]
        print(f"Selecting computers: {[c.id for c in selected]}")
        for comp in selected:
            # Create PrestamoDetalle records (this is what makes the computer considered as having an active loan)
            detalle = PrestamoDetalle(
                prestamo_id=loan.id,
                computadora_id=comp.id,
                hora_devolucion_real=None
            )
            db.session.add(detalle)
            # Do NOT change comp.estado here; let update_estados compute it.
        db.session.commit()
        print("Loan details created.")
        # Now run the update_estados function to see what states we get
        from update_estados import update_estados
        update_estados()
        print("\nAfter update_estados:")
        for comp in selected:
            print(f"  Computer {comp.id}: estado={comp.estado}")
        # Also check all computers for solicitado
        solicitados = [c for c in computers if c.estado == 'solicitado']
        print(f"\nSolicitado computers: {[c.id for c in solicitados]}")
        prestados = [c for c in computers if c.estado == 'prestado']
        print(f"Prestado computers: {[c.id for c in prestados]}")
        disponibles = [c for c in computers if c.estado == 'disponible' and not c.mantenimiento]
        print(f"Disponible computers: {len(disponibles)} (first few: {[c.id for c in disponibles[:5]]})")