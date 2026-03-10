from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.dependencies.knowledge_units_factory import get_knowledge_units_factory
from app.core.dependencies.llm_client import init_openai_client
from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.knowledge_unit_factory.knowledge_units import KnowledgeUnitsFactory
from app.repository.database import PostgresPool
from app.config import config
from app.utils import database
from app.core.dependencies import logging
from app.api.app_router import api_router
import uvicorn
from app.core.dependencies.azure_storage import init_azure_storage_service
from app.core.dependencies.knowledge_units_factory import init_knowledge_unit_factory
from app.core.dependencies.embedders import init_text_embedder, init_image_embedder

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

# TRYING LOCAL DATABASE CONFIG SUCCESSFUL
local_db_config = config.local_db

dsn = database.generate_dsn(
    local_db_config.host,
    local_db_config.port,
    local_db_config.username,
    local_db_config.password,
    local_db_config.db_name
)


PostgresPool.init(dsn)
text_embedder = init_text_embedder()
image_embedder = init_image_embedder()
openai_client = init_openai_client()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.text_embedder = text_embedder
    app.state.openai_client = openai_client
    app.state.image_embedder = image_embedder
    storage = init_azure_storage_service()
    app.state.azure_storage_service = storage
    knowledge_units_factory = init_knowledge_unit_factory(
        text_embedder=text_embedder,
        image_embedder=image_embedder,
        storage=storage,
    )
    app.state.knowledge_units_factory = knowledge_units_factory
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