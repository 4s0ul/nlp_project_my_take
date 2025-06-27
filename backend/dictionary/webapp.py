from loguru import logger
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dictionary.database.models import *
from dictionary.database.engine import init_db
from dictionary.misc.utils import check_nltk_resource
from dictionary.routers import (
    topics_router,
    terms_router,
    descriptions_router,
    triplets_router,
    graphs_router,
)


routers = [
    topics_router.router,
    terms_router.router,
    descriptions_router.router,
    triplets_router.router,
    graphs_router.router,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    if check_nltk_resource("tokenizers/punkt"):
        logger.info("Punkt tokenizer is installed.")
    else:
        logger.warning("Punkt tokenizer is NOT installed.")

    if check_nltk_resource("corpora/stopwords"):
        logger.info("Stopwords corpus is installed.")
    else:
        logger.warning("Stopwords corpus is NOT installed.")

    logger.info("Initializing database")
    await init_db()
    logger.info("Database initialized OK")

    yield


app = FastAPI(
    root_path=os.environ.get("APP_PREFIX", "/"),
    swagger_ui_parameters={"operationsSorter": "method"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in routers:
    app.include_router(r)
