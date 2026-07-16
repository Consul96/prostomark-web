from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import admin, analytics, auth, billing, calculations, dashboard, documents, marking, products
from app.services.marking.errors import MarkingError


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    api_prefix = settings.api_v1_prefix
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(products.router, prefix=api_prefix)
    app.include_router(documents.router, prefix=api_prefix)
    app.include_router(calculations.router, prefix=api_prefix)
    app.include_router(dashboard.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)
    app.include_router(billing.router, prefix=api_prefix)
    app.include_router(marking.router, prefix=api_prefix)

    @app.exception_handler(MarkingError)
    async def _marking_error_handler(_: Request, exc: MarkingError) -> JSONResponse:
        return JSONResponse(status_code=exc.http_status, content=exc.to_dict())

    @app.get('/health', tags=['health'])
    def health() -> dict[str, str]:
        return {'status': 'ok'}

    return app


app = create_app()
