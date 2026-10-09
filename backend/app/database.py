from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# L'engine gère la connexion (et le pool de connexions) vers MySQL.
# pool_pre_ping=True teste la connexion avant de s'en servir, ce qui évite
# les erreurs quand MySQL a fermé une connexion restée inactive.
# connect_args passe le certificat CA au driver PyMySQL pour chiffrer la
# connexion (SSL) et vérifier l'identité du serveur Aiven.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"ssl": {"ca": settings.ca_cert_path}},
)

# Fabrique de sessions. Une session = une "conversation" avec la base
# (requêtes + transaction). autoflush=False : rien n'est envoyé à la base
# tant qu'on ne le demande pas explicitement.
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# Classe parente de tous les modèles SQLAlchemy (tables).
# Chaque modèle héritera de Base : `class User(Base): ...`
class Base(DeclarativeBase):
    pass


# Dépendance FastAPI : ouvre une session pour la durée d'une requête,
# la fournit à l'endpoint (yield), puis la ferme quoi qu'il arrive (finally).
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
