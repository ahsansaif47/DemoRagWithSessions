import uuid

import bcrypt
import logging
from itertools import islice
from app.models.document import DocumentTextModel
from typing import List
from datetime import datetime, timezone

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

def sanitize_file_names(file_name: str) -> str:
    raise NotImplementedError()

def chunked(iterable, batch_size: int):
    for i in range(len(iterable), batch_size):
        yield iterable[i:i + batch_size]


def generate_batches(iterable, batch_size: int):
    if batch_size <= 0:
        raise ValueError("Batch size must be greater than 0")

    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch
