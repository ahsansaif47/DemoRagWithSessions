from app.repository.database import PostgresPool
from app.core.pdf_extractor import text_extractor
from app.config import config
from app.utils import database
import logging
from app.core.dependencies import logging


# FIXME: Get the extractor out of the core package
# TODO: Create an extractor package and place it there

# Logger setup in the main file
logging.setup_logger()



# LOADING APPLICATION CONFIG
config = config.AppConfig()

# ------------------------
# Logging Configuration
# ------------------------




# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s"
# )
# logger = logging.getLogger(__name__)

# TRYING LOCALDATABASE CONFIG SUCCESSFUL
local_db_config = config.local_db

dsn = database.generate_dsn(
    local_db_config.host,
    local_db_config.port,
    local_db_config.username,
    local_db_config.password,
    local_db_config.db_name
)


PostgresPool.init(dsn)


if __name__ == '__main__':
    print('PyCharm')
    with PostgresPool.get_local_pool().connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            print(cursor.fetchall())