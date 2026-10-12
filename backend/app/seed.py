"""Explicit local initialization: python -m app.seed [--demo] [--admin-email ...]."""

import argparse
from getpass import getpass

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Advertisement, Company, Person
from app.models.advertisement import AdvertisementStatus, ContractType
from app.models.auth import AuthSession, Credential  # noqa: F401
from app.models.person import PersonRole
from app.security import hash_password


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--admin-email")
    args = parser.parse_args()
    # Adds missing tables only. Existing production tables are never dropped.
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if args.admin_email:
            email = args.admin_email.lower()
            if db.scalar(select(Person).where(Person.email == email)):
                raise SystemExit(
                    "Adresse déjà existante : aucune modification effectuée."
                )
            password = getpass("Mot de passe administrateur (10 caractères minimum) : ")
            if len(password) < 10 or len(password) > 128:
                raise SystemExit("Mot de passe invalide.")
            person = Person(
                firstname="Admin",
                lastname="Jobboard",
                email=email,
                role=PersonRole.admin,
            )
            db.add(person)
            db.flush()
            db.add(
                Credential(people_id=person.id, password_hash=hash_password(password))
            )
        if args.demo and not db.scalar(select(Company.id).limit(1)):
            for name, city in [("HireLoop", "Paris"), ("Atelier Web", "Lyon")]:
                company = Company(
                    name=name,
                    city=city,
                    country="France",
                    description="Entreprise de démonstration",
                )
                db.add(company)
                db.flush()
                for title in ["Développeur React", "Développeur Python"]:
                    db.add(
                        Advertisement(
                            title=title,
                            short_description=(
                                f"Rejoignez {name} et développez "
                                "des applications utiles."
                            ),
                            full_description=(
                                "Au sein de notre équipe, vous développerez des "
                                "fonctionnalités, écrirez des tests et participerez "
                                "aux revues de code. Accompagnement et télétravail "
                                "partiel proposés."
                            ),
                            salary=38000,
                            location=city,
                            working_time="35 heures / semaine",
                            contract_type=ContractType.cdi,
                            status=AdvertisementStatus.published,
                            company_id=company.id,
                        )
                    )
        db.commit()
    print("Tables prêtes. Données demandées enregistrées.")


if __name__ == "__main__":
    main()
