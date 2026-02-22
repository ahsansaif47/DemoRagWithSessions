
def generate_dsn(host: str, port: int, username: str, password: str, db_name: str) -> str:
    return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"