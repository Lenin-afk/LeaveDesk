from app.database import SessionLocal
from app.models import User
from app.security import hash_password

db = SessionLocal()

priya = User(
    name="Priya",
    email="priya.manager@leavedesk.test",
    password_hash=hash_password("Manager@123"),
    role="manager",
    manager_id=None
)

db.add(priya)
db.commit()
db.refresh(priya)

arjun = User(
    name="Arjun",
    email="arjun@leavedesk.test",
    password_hash=hash_password("Employee@123"),
    role="employee",
    manager_id=priya.id
)

meera = User(
    name="Meera",
    email="meera@leavedesk.test",
    password_hash=hash_password("Employee@123"),
    role="employee",
    manager_id=priya.id
)

db.add_all([arjun, meera])
db.commit()
db.close()
