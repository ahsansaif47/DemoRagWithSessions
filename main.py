from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.repository.database import PostgresPool
from app.config import config
from app.utils import database
from app.core.dependencies import logging
from app.api.app_router import api_router
import uvicorn
from app.core.dependencies.azure_storage import get_azure_storage_service


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

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.azure_storage_service = get_azure_storage_service
    yield




app = FastAPI(title="Demo Rag With Sessions", lifespan=lifespan)
app.include_router(api_router)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")

    # print('PyCharm')
    # with PostgresPool.get_local_pool().connection() as connection:
    #     with connection.cursor() as cursor:
    #         cursor.execute("SELECT NOW();")
    #         print(cursor.fetchall())