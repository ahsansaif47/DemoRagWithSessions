import bcrypt
import logging

logger = logging.getLogger(__name__)


def generate_password_hash(password: str) -> str:
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f'Password Hash Failed: {str(e)}')
        return ""

def verify_password(password: str, hashed_password: str) -> bool | None:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f'Password/Hash Comparison Failed: {str(e)}')
        return None
