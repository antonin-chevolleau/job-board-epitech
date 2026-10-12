from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.routers import admin, advertisements, auth

# L'application FastAPI : point d'entrée lancé par `fastapi dev main.py`
app = FastAPI()

# CORS : par défaut, un navigateur bloque les appels d'un site (le front sur
# localhost:5173) vers une autre adresse (l'API sur :8000). Ce middleware
# ajoute les en-têtes qui autorisent les origines listées dans la config.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # autorise l'envoi de cookies / en-têtes d'auth
    allow_methods=["*"],  # GET, POST, PUT, DELETE...
    allow_headers=["*"],
)


# Branche les routes de /advertisements sur l'application
app.include_router(advertisements.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    errors = exc.errors()
    # Bootstrap: missing required fields -> 400; other invalid values -> 422.
    # Do not echo submitted values (especially passwords) in error responses.
    return JSONResponse(
        status_code=400 if any(e["type"] == "missing" for e in errors) else 422,
        content={
            "detail": [
                {"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in errors
            ]
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error(request, exc):
    # Do not disclose SQL queries, credentials or personal data.
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Cet enregistrement existe déjà ou une relation est invalide."
        },
    )


# Route de test : GET http://127.0.0.1:8000/
@app.get("/")
async def root():
    return {"message": "Hello World!"}


# Route de santé : vérifie que l'API tourne ET que la base répond.
# `Depends(get_db)` demande à FastAPI de nous fournir une session de base
# de données (ouverte avant la requête, fermée après).
@app.get("/health")
def health(db: Annotated[Session, Depends(get_db)]):
    # Requête minimale : lève une erreur si MySQL est injoignable
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
