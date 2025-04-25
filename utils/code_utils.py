import random

from models import User

def generate_unique_4digit(db):
    while True:
        code = str(random.randint(1000, 9999))
        existing = db.query(User).filter_by(unique_code=code).first()
        if not existing:
            return code
