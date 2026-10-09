from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.routers import advertisements

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
