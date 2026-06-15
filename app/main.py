from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings
from app.middleware.logging_mw import LoggingMiddleware
from app.middleware.security_headers_mw import SecurityHeadersMiddleware
from app.middleware.rate_limit_mw import RateLimitMiddleware
from app.db.init_db import init_db
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
import re

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=settings.PROJECT_NAME, version="1.0.0", routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

# 2. CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 3. GZIP — compress responses > 1KB automatically
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. SECURITY HEADERS
app.add_middleware(SecurityHeadersMiddleware)

# 5. RATE LIMITING
app.add_middleware(RateLimitMiddleware)

# 6. LOGGING
app.add_middleware(LoggingMiddleware)

# ROUTING: Main API endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please contact support."}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Extract clean message and errors
    err_msg = ""
    err_list = None
    if isinstance(exc.detail, dict):
        err_msg = exc.detail.get("message", "An error occurred")
        err_list = exc.detail.get("errors")
    else:
        err_msg = str(exc.detail)

    content = {
        "message": err_msg,
        "error": err_msg,
        "detail": err_msg
    }
    if err_list:
        content["errors"] = err_list

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors_list = []
    field_errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "field"
        message = error.get("msg", "")
        err_type = error.get("type", "unknown")
        
        # Convert field to user-friendly label
        field_str = str(field)
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', field_str)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        field_label = s2.replace("_", " ").strip().title()
        
        # Format a short, clear error message
        # If the field is missing or passed as None (null) for a non-nullable field, treat it as a required field error
        if err_type == "missing" or message == "Field required" or error.get("input") is None:
            clean_msg = f"{field_label} is a required field"
            field_errors.append(clean_msg)
        else:
            if "int" in err_type or "decimal" in err_type or "float" in err_type:
                clean_msg = "All integers should be used"
            elif message.startswith("Value error, "):
                clean_msg = message[len("Value error, "):]
            elif message.startswith("Assertion failed, "):
                clean_msg = message[len("Assertion failed, "):]
            else:
                clean_msg = message
            field_errors.append(f"{field_label}: {clean_msg}")
        
        # Keep structured errors format as fallback/legacy format
        full_field_path = " -> ".join([str(loc) for loc in error["loc"] if loc != "body"])
        errors_list.append({
            "field": full_field_path,
            "error_type": err_type,
            "message": clean_msg
        })

    error_summary = "; ".join(field_errors) if field_errors else "Validation failed"
    
    return JSONResponse(
        status_code=422,
        content={
            "message": error_summary,
            "error": error_summary,
            "detail": error_summary,
            "errors": field_errors,
            "missing_or_invalid_fields": errors_list
        }
    )

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "message": f"{settings.PROJECT_NAME} is running",
        "version": "1.0.0"
    }