from pydantic_settings import BaseSettings, SettingsConfigDict


# Regroupe tous les réglages de l'application.
# Pydantic remplit chaque champ avec la variable d'environnement du même nom
# (database_url <- DATABASE_URL), lue dans le fichier .env.
class Settings(BaseSettings):
    # URL de connexion à MySQL, obligatoire : pas de valeur par défaut,
    # donc l'app refuse de démarrer si elle est absente du .env
    database_url: str
    # Certificat CA d'Aiven : permet de vérifier qu'on parle bien à notre serveur
    # MySQL (connexion SSL). Chemin relatif au dossier backend/.
    ca_cert_path: str = "certs/ca.pem"
    # Sites autorisés à appeler l'API depuis un navigateur (le front React).
    # Valeur par défaut : le serveur de dev de Vite.
    cors_origins: list[str] = ["http://localhost:5173"]

    # Indique à Pydantic de charger les valeurs depuis le fichier .env
    model_config = SettingsConfigDict(env_file=".env")


# Instance unique, importée partout : `from app.config import settings`
settings = Settings()
