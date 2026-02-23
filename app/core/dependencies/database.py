from app.repository.database import get_database_connection


def get_database():
    db = get_database_connection()
    try:
        yield db
    finally:
        db.close()
