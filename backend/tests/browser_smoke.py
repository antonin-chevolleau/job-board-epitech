"""Run explicitly: python tests/browser_smoke.py (requires Playwright Chromium).

Starts both servers on dedicated ports, uses a temporary SQLite DB, then stops them.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BACKEND = Path(__file__).resolve().parents[1]
FRONTEND = BACKEND.parent / "frontend"
API = "http://127.0.0.1:18000"
WEB = "http://127.0.0.1:15173"


def wait_for(url):
    for _ in range(100):
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)
    raise RuntimeError(f"Server did not start: {url}")


def main():
    with tempfile.TemporaryDirectory(prefix="jobboard-e2e-") as directory:
        env = {
            **os.environ,
            "DATABASE_URL": f"sqlite:///{directory}/test.db",
            "CA_CERT_PATH": "",
            "CORS_ORIGINS": json.dumps([WEB]),
            "VITE_API_URL": API,
        }
        subprocess.run(
            [sys.executable, "-m", "app.seed", "--demo"],
            cwd=BACKEND,
            env=env,
            check=True,
        )
        # Only this disposable test database receives a known admin password.
        subprocess.run(
            [
                sys.executable,
                "-c",
                """
from app.database import SessionLocal
from app.models import Person
from app.models.auth import Credential
from app.models.person import PersonRole
from app.security import hash_password
with SessionLocal() as db:
    p = Person(firstname="Admin", lastname="Test",
               email="admin@example.com", role=PersonRole.admin)
    db.add(p)
    db.flush()
    db.add(Credential(people_id=p.id, password_hash=hash_password("admin-password")))
    db.commit()
""",
            ],
            cwd=BACKEND,
            env=env,
            check=True,
        )
        processes = []
        with open(Path(directory) / "servers.log", "w+") as log:
            try:
                processes.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "uvicorn",
                            "main:app",
                            "--host",
                            "127.0.0.1",
                            "--port",
                            "18000",
                        ],
                        cwd=BACKEND,
                        env=env,
                        stdout=log,
                        stderr=log,
                    )
                )
                processes.append(
                    subprocess.Popen(
                        [
                            "node",
                            "node_modules/vite/bin/vite.js",
                            "--host",
                            "127.0.0.1",
                            "--port",
                            "15173",
                            "--strictPort",
                        ],
                        cwd=FRONTEND,
                        env=env,
                        stdout=log,
                        stderr=log,
                    )
                )
                wait_for(f"{API}/health")
                wait_for(WEB)
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch()
                    page = browser.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(WEB)
                    expect(page.locator("article")).to_have_count(4)
                    url = page.url
                    page.locator("article").first.get_by_role(
                        "button", name="En savoir plus"
                    ).click()
                    expect(
                        page.get_by_role("heading", name="Description du poste")
                    ).to_be_visible()
                    assert page.url == url
                    # Guest application is persisted and visible to the admin later.
                    card = page.locator("article").first
                    card.get_by_role("button", name="Postuler", exact=True).click()
                    card.get_by_label("Prénom", exact=True).fill("Guest")
                    card.get_by_label("Nom", exact=True).fill("Visitor")
                    card.get_by_label("Email", exact=True).fill("guest@example.com")
                    card.get_by_label("Message au recruteur").fill(
                        "Candidature visiteur"
                    )
                    card.get_by_role("button", name="Envoyer ma candidature").click()
                    expect(card.get_by_role("status")).to_contain_text("enregistrée")
                    page.get_by_role("link", name="Connexion", exact=True).click()
                    page.get_by_role("link", name="Créer un compte", exact=True).click()
                    page.get_by_label("Prénom", exact=True).fill("Ada")
                    page.get_by_label("Nom", exact=True).fill("Lovelace")
                    page.get_by_label("Email", exact=True).fill("ada@example.com")
                    page.get_by_label("Téléphone", exact=True).fill("0600000000")
                    page.get_by_label("Mot de passe").fill("candidate-password")
                    page.get_by_role("button", name="Enregistrer", exact=True).click()
                    expect(page).to_have_url(f"{WEB}/Annonces")
                    card = page.locator("article").first
                    card.get_by_role("button", name="Postuler", exact=True).click()
                    expect(
                        card.get_by_text("Vous postulez en tant que Ada Lovelace")
                    ).to_be_visible()
                    card.get_by_label("Message au recruteur").fill(
                        "Candidature connectée"
                    )
                    card.get_by_role("button", name="Envoyer ma candidature").click()
                    expect(card.get_by_role("status")).to_contain_text("enregistrée")
                    page.get_by_role("link", name="Mon compte").click()
                    page.get_by_label("Prénom", exact=True).fill("Grace")
                    page.get_by_role("button", name="Enregistrer", exact=True).click()
                    expect(page.get_by_role("status")).to_contain_text("mis à jour")
                    page.reload()
                    expect(page.get_by_label("Prénom", exact=True)).to_have_value(
                        "Grace"
                    )
                    page.goto(f"{WEB}/Admin")
                    expect(page).to_have_url(f"{WEB}/Annonces")
                    page.get_by_role("button", name="Déconnexion").click()
                    page.get_by_role("link", name="Connexion", exact=True).click()
                    page.get_by_label("Email", exact=True).fill("admin@example.com")
                    page.get_by_label("Mot de passe", exact=True).fill("admin-password")
                    page.get_by_role("button", name="Se connecter", exact=True).click()
                    expect(page).to_have_url(f"{WEB}/Admin")
                    page.get_by_role("button", name="Candidatures", exact=True).click()
                    expect(
                        page.get_by_role(
                            "cell", name="Candidature visiteur", exact=True
                        )
                    ).to_be_visible()
                    expect(
                        page.get_by_role(
                            "cell", name="Candidature connectée", exact=True
                        )
                    ).to_be_visible()
                    page.get_by_role("button", name="Modifier #1", exact=True).click()
                    page.get_by_label("Statut", exact=True).select_option("accepted")
                    page.get_by_role("button", name="Enregistrer", exact=True).click()
                    expect(
                        page.get_by_role("cell", name="accepted", exact=True)
                    ).to_be_visible()
                    page.get_by_role("button", name="Entreprises", exact=True).click()
                    page.get_by_role("button", name="Créer", exact=True).click()
                    page.get_by_label("Nom", exact=True).fill("Browser company")
                    page.get_by_role("button", name="Enregistrer", exact=True).click()
                    row = page.get_by_role("row").filter(has_text="Browser company")
                    expect(row).to_be_visible()
                    row.get_by_role("button", name="Supprimer #3", exact=True).click()
                    page.get_by_role("button", name="Confirmer la suppression").click()
                    expect(row).to_have_count(0)
                    # Narrow-screen rendering must not overflow the viewport.
                    page.get_by_role("link", name="Annonces", exact=True).click()
                    page.set_viewport_size({"width": 390, "height": 844})
                    expect(page.locator("article")).to_have_count(4)
                    assert page.evaluate(
                        "document.documentElement.scrollWidth <= innerWidth"
                    )
                    assert not errors, errors
                    browser.close()
                print(
                    "Browser smoke passed: guest, account, details, "
                    "applications, admin CRUD, mobile."
                )
            except Exception:
                log.flush()
                log.seek(0)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                for process in processes:
                    process.terminate()
                for process in processes:
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


if __name__ == "__main__":
    main()
