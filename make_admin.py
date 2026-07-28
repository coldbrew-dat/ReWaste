from app import app
from models.db import db
from models.models import User

with app.app_context():
    admin = User(
        business_name="Admin",
        email="admin@rewaste.pk",
        is_admin=True,
    )
    admin.set_password("12#")
    db.session.add(admin)
    db.session.commit()
    print("Admin account created:", admin.email)
