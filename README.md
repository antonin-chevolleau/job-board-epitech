# JobBoard — Epitech

Job board **React + FastAPI + SQLAlchemy + MySQL**, tout en local.
Sujet : `sujets/jobBoard-project.pdf` (guide : `sujets/jobBoard-bootstrap.pdf`).

Le backend est la source de vérité du contrat d'API : sa documentation détaillée
(routes, schéma, configuration) est dans [`backend/README.md`](backend/README.md)
et dans Swagger (<http://127.0.0.1:8000/docs>).

## Lancer en local

Prérequis : **Python 3.12+**, **Node.js 22.12+**, **MySQL 8** en local.
Guide pas à pas : [`docs/setup-local.md`](docs/setup-local.md).

### 1. Base de données

```bash
mysql -u <user> -p -e "CREATE DATABASE job_board CHARACTER SET utf8mb4;"
mysql -u <user> -p job_board < backend/sql/schemas.sql   # ATTENTION : supprime et recrée les tables
mysql -u <user> -p job_board < backend/sql/seed.sql      # données de démonstration
```

Comptes du seed (mot de passe `admin1234`) : `admin` (admin), `recruiter`, `jdoe` (user).

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # renseigner DATABASE_URL et SECRET_KEY
python -m uvicorn app.main:app --reload --port 8000
```

- API : <http://127.0.0.1:8000/api>
- Swagger : <http://127.0.0.1:8000/docs>
- Santé : <http://127.0.0.1:8000/health>

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # seulement si vous n'avez pas déjà de .env
npm run dev
```

Ouvrir l'URL affichée par Vite (port 5173). `VITE_API_URL` pointe vers le backend
**sans** suffixe `/api` (défaut `http://127.0.0.1:8000`) ; le front ajoute `/api`.
L'origine du front doit figurer dans `CORS_ORIGINS` (`backend/.env`).

## Pages

| URL | Fonction |
| --- | --- |
| `/`, `/Annonces` | Liste paginée, recherche (mot-clé, lieu, contrat) faite par l'API, détails à la demande, candidature |
| `/CreateAccount` | Inscription puis connexion automatique |
| `/Login` | Connexion (nom d'utilisateur ou email) ; admin → `/Admin`, sinon `/Annonces` |
| `/Account` | Coordonnées modifiables, connexion requise |
| `/Admin` | CRUD paginé des annonces, entreprises, utilisateurs et candidatures (admin) |

## API en bref

Toutes les routes sont sous `/api`. Détail complet : [`backend/README.md`](backend/README.md).

- **Auth** : JWT Bearer (60 min par défaut), mots de passe bcrypt. `POST /auth/login`
  attend un formulaire (`username`, `password`). Pas de route de déconnexion : le front
  supprime le jeton (`sessionStorage`).
- **Listes** : `page` (défaut 1) et `limit` (défaut 20, max 100), réponse
  `{ "items": [...], "total": n, "page": 1, "limit": 20 }`.
- **Mise à jour** : `PUT` = remplacement complet (tous les champs, `null` pour vider).
- **Rôles** : `user`, `recruiter`, `admin`. Les écritures et les routes `/users` et
  `/applications` sont réservées à l'admin (le rôle `recruiter` n'a pas encore de droits propres).
- **Candidature** : `POST /advertisements/{id}/applications`, anonyme ou connecté.
  Un utilisateur connecté postule toujours avec l'email de son compte ; un visiteur
  ne peut pas utiliser l'email d'un compte existant. Une candidature par email et par annonce.
- **Limitation de débit** : login et candidature, par IP (`429` + `Retry-After`).
- **Email** : notification au propriétaire de l'annonce si `SMTP_HOST` est configuré.

## Modèle SQL

`companies`, `users`, `advertisements`, `job_applications` — voir
[`docs/data-models.md`](docs/data-models.md). Le schéma de référence est
`backend/sql/schemas.sql` ; les modèles SQLAlchemy le reflètent.

## Tests

```bash
cd backend && .venv/bin/pytest          # sur la base du .env, seedée avec sql/seed.sql
cd frontend && npm run lint && npm run build
```

Les tests backend utilisent la base MySQL configurée dans `.env` (comptes du seed)
et suppriment les enregistrements qu'ils créent.
