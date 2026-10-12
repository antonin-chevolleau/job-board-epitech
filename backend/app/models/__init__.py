# Tous les modèles sont importés ici : SQLAlchemy doit les connaître pour
# résoudre les relationships (ex. "Company" référencé depuis Advertisement).
from app.models.advertisement import Advertisement
from app.models.application import Application
from app.models.company import Company
from app.models.person import Person

__all__ = ["Advertisement", "Application", "Company", "Person"]
