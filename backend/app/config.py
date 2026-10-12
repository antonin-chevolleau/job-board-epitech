from pydantic_settings import BaseSettings, SettingsConfigDict


# Regroupe tous les réglages de l'application.
# Pydantic remplit chaque champ avec la variable d'environnement du même nom
# (database_url <- DATABASE_URL), lue dans le fichier .env.
class Settings(BaseSettings):
    # SQLite pour le développement ; MySQL reste configurable via .env.
    database_url: str = "sqlite:///./jobboard.db"
    # Certificat CA d'Aiven : permet de vérifier qu'on parle bien à notre serveur
    # MySQL (connexion SSL). Chemin relatif au dossier backend/.
    ca_cert_path: str = ""
    session_hours: int = 12
    # Sites autorisés à appeler l'API depuis un navigateur (le front React).
    # Valeur par défaut : le serveur de dev de Vite.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Indique à Pydantic de charger les valeurs depuis le fichier .env
    model_config = SettingsConfigDict(env_file=".env")


# Instance unique, importée partout : `from app.config import settings`
settings = Settings()
