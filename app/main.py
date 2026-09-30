from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.config import get_settings

from app.database import (
    Base,
    engine
)

from app.routes import (
    api,
    auth,
    pages,
    planners,
)


settings = get_settings()


@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    Base.metadata.create_all(
        bind=engine
    )

    yield


app = FastAPI(

    title=settings.app_name,

    description=(
        "Budget-aware AI "
        "recommendation assistant "
        "for home, party, "
        "and jewelry planning."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


# Serve CSS, JavaScript and other static files
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=
        settings.cors_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(
    pages.router
)

app.include_router(
    auth.router
)

app.include_router(
    planners.router
)

app.include_router(
    api.router
)


@app.get("/health")
def health():

    return {
        "status": "ok",

        "app":
            settings.app_name,

        "ai_configured":
            bool(
                settings.gemini_api_key
            ),
    }


@app.get("/startup")
def startup():

    return {
        "status":
            "initialized",

        "environment":
            settings.environment,
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )