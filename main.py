import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import public
from api.routers.dependencies import get_database


def validate_environment_variables(required_variables):
    missing_variables = [variable for variable in required_variables if os.getenv(variable) is None]
    if missing_variables:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_variables)}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # app startup
    required_environment_variables = ['IPSTACK_KEY', 'DATABASE_URI']
    validate_environment_variables(required_environment_variables)
    database = await get_database()
    await database.create_tables()
    yield
    # app teardown


load_dotenv()

app = FastAPI(lifespan=lifespan)


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    public.router,
    prefix="/api/v1/public",
    tags=["public"],
)
