# Job Board | Backend

API REST du projet Job Board (voir `../sujets/jobBoard-project.pdf`) : annonces, entreprises,
utilisateurs, authentification et candidatures, stockés dans MySQL.

Stack : **Python 3.12+**, **FastAPI**, **SQLAlchemy 2**, **MySQL 8**, JWT (PyJWT) et bcrypt.

## Installation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt        # requirements-dev.txt en plus pour lancer les tests
```

## Configuration

### 1. Base de données

Créer une base vide, puis charger le schéma et les données de démonstration :

```bash
mysql -u <user> -p -e "CREATE DATABASE job_board CHARACTER SET utf8mb4;"
mysql -u <user> -p job_board < sql/schemas.sql   # ATTENTION : supprime et recrée toutes les tables
mysql -u <user> -p job_board < sql/seed.sql      # facultatif : données de démonstration
```

Comptes du seed (mot de passe `admin1234` pour tous, **à changer hors développement**) :

| user_name   | rôle        | remarques                       |
| ----------- | ----------- | ------------------------------- |
| `admin`     | `admin`     | accès aux routes d'admin        |
| `recruiter` | `recruiter` | auteur des annonces d'Acme Tech |
| `jdoe`      | `user`      | candidat classique              |

### 2. Environnement

```bash
cp .env.example .env
```

| Variable                          | Obligatoire | Description                                                                                 |
| --------------------------------- | ----------- | ------------------------------------------------------------------------------------------- |
| `DATABASE_URL`                    | oui         | `mysql+pymysql://USER:PASSWORD@localhost:3306/job_board`                                    |
| `SECRET_KEY`                      | oui         | Clé de signature des JWT, 32 caractères minimum ; la valeur de `.env.example` est refusée   |
| `ACCESS_TOKEN_EXPIRE_MINUTES`     | non         | Durée de vie du jeton, défaut `60`                                                          |
| `CORS_ORIGINS`                    | non         | Origines du front séparées par des virgules, défaut : Vite sur le port 5173                 |
| `RATE_LIMIT_ENABLED`              | non         | Défaut `true`                                                                               |
| `RATE_LIMIT_LOGIN`                | non         | Tentatives de connexion par IP client, défaut `10/minute`                                   |
| `RATE_LIMIT_APPLY`                | non         | Candidatures par IP client, défaut `20/hour`                                                |
| `SMTP_HOST`                       | non         | Active l'email envoyé au propriétaire de l'annonce à chaque candidature                     |
| `SMTP_PORT`                       | non         | Défaut `587`                                                                                |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | non         | Identifiants SMTP                                                                           |
| `SMTP_FROM`                       | non         | Adresse d'expédition, défaut `noreply@jobboard.local`                                       |
| `SMTP_STARTTLS`                   | non         | Défaut `true`                                                                               |

Générer une clé avec `python3 -c "import secrets; print(secrets.token_hex(32))"`.
`.env` est ignoré par git : ne jamais commiter de vrais identifiants.

## Lancement

```bash
.venv/bin/uvicorn app.main:app --reload
```

- API : <http://localhost:8000/api>
- Documentation interactive (Swagger) : <http://localhost:8000/docs>
- Santé : <http://localhost:8000/health>

## Tests

```bash
.venv/bin/pytest
```

Les tests tournent sur la base configurée dans `.env` (seedée avec `sql/seed.sql`, ils se connectent en
`admin` / `admin1234`). Chaque test supprime les enregistrements qu'il crée.

## Structure du projet

```bash
.
|--- sql/
|    |--- schemas.sql # schéma de la base (source de vérité, supprime les tables existantes)
|    |--- seed.sql # données de démonstration
|--- app/
|    |--- main.py # application FastAPI, CORS, /health
|    |--- core/ # config.py (réglages du .env), database.py (moteur, session), security.py (bcrypt, JWT), rate_limit.py (fenêtre glissante)
|    |--- models/ # modèles SQLAlchemy, un fichier par table (miroir de sql/schemas.sql)
|    |--- schemas/ # modèles Pydantic de requête / réponse, un fichier par ressource (+ common, auth)
|    |--- api/
|    |    |--- router.py #  monte toutes les routes sous /api
|    |    |--- deps.py #  dépendances : session BDD, utilisateur courant, contrôle admin
|    |    |--- pagination.py #  paramètres page / limit et paginate()
|    |    |--- rate_limit.py #  dépendances de limitation de débit par IP (connexion, candidature)
|    |    |--- errors.py #  get_or_404 et erreurs d'intégrité MySQL converties en erreurs HTTP
|    |    |--- routes/ #  auth, companies, advertisements, users, applications
|    |--- services/
|    |    |--- emailer.py # notification SMTP facultative des candidatures
|--- tests/ # tests pytest de l'API (sur la base du .env)
```

## Schéma de la base

```
companies 1 ──< users                 (users.company_id, ON DELETE SET NULL)
companies 1 ──< advertisements        (ON DELETE CASCADE)
users     1 ──< advertisements        (advertisements.user_id = auteur, ON DELETE SET NULL)
advertisements 1 ──< job_applications (ON DELETE CASCADE)
users     1 ──< job_applications      (job_applications.user_id, nullable : anonyme, ON DELETE SET NULL)
```

| Table              | Colonnes principales                                                                                                                                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `companies`        | `name` (unique), `description`, `email` (unique), `phone`, `address`, `city`, `country`                                                                                                                                 |
| `users`            | `user_name` (unique), `hashed_password`, `first_name`, `last_name`, `email` (unique), `phone`, `role` (`user`/`recruiter`/`admin`), `company_id`                                                                        |
| `advertisements`   | `company_id`, `user_id`, `title`, `short_description`, `full_description`, `location`, `salary`, `contract_type` (`CDI`/`CDD`/`Stage`/`Alternance`/`Freelance`), `working_time`, `is_active`                            |
| `job_applications` | `advertisement_id`, `user_id`, `applicant_name`, `applicant_email`, `applicant_phone`, `message`, `status` (`pending`/`reviewed`/`accepted`/`rejected`), `email_sent_at` ; unique (`advertisement_id`, `applicant_email`) |

Chaque table a aussi `id`, `created_at` et `updated_at`.

## API

Toutes les routes sont préfixées par `/api`. Les routes authentifiées attendent `Authorization: Bearer <token>`.

### Conventions

- **Pagination** : les routes de liste acceptent `page` (défaut `1`) et `limit` (défaut `20`, max `100`) et
  renvoient `{ "items": [...], "total": 42, "page": 1, "limit": 20 }`.
- **Mise à jour** : `PUT` remplace toute la ressource : chaque champ doit être envoyé, les facultatifs en
  `null` (omettre un champ donne un `422`, rien n'est réinitialisé en silence). Seule exception : `password`
  sur `PUT /users/{id}`, inchangé s'il est omis.
- **Limitation de débit** : `POST /api/auth/login` et `POST /api/advertisements/{id}/applications` sont
  limitées par IP client (`RATE_LIMIT_LOGIN`, `RATE_LIMIT_APPLY`) ; chaque tentative compte, réussie ou non.
  Au-delà de la limite, l'API répond `429` avec un en-tête `Retry-After` (en secondes). Les compteurs sont
  en mémoire du processus : avec plusieurs workers, chacun compte de son côté. Derrière un reverse proxy,
  lancer uvicorn avec `--forwarded-allow-ips=<ip du proxy>` pour utiliser l'IP réelle du client et non
  celle du proxy.
- **Jetons** : un jeton invalide ou expiré est traité comme « non connecté » : les routes publiques
  fonctionnent toujours, les routes protégées répondent `401`.
- **Suppression** : `204 No Content`.
- **Erreurs** : `401` non authentifié, `403` pas admin, `404` introuvable, `429` trop de requêtes, `409`
  valeur en double ou enregistrement encore référencé, `422` corps invalide (trop long, hors limites, champ
  manquant) ou référence à un enregistrement inexistant.

### Authentification

| Méthode | Route                | Accès     | Description                                                                                                    |
| ------- | -------------------- | --------- | -------------------------------------------------------------------------------------------------------------- |
| POST    | `/api/auth/register` | public    | Crée un compte `user` (`user_name` ne peut pas contenir `@`)                                                   |
| POST    | `/api/auth/login`    | public    | Champs de formulaire `username` (nom d'utilisateur ou email) et `password` ; renvoie `access_token`, `role`, `user_id` |
| GET     | `/api/auth/me`       | connecté  | Profil courant                                                                                                 |
| PUT     | `/api/auth/me`       | connecté  | Modifie le profil ; `new_password` exige `current_password`                                                    |

Le front redirige vers la page d'administration quand le `role` renvoyé est `admin`.

### Annonces

| Méthode | Route                                   | Accès                | Description                                                                                                                                         |
| ------- | --------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET     | `/api/advertisements`                   | public               | Liste (sans `full_description`). Filtres : `q` (titre, description courte), `location`, `contract_type`, `company_id`, `is_active` (admin seulement) |
| GET     | `/api/advertisements/{id}`              | public               | Détail complet, utilisé par le bouton « En savoir plus »                                                                                            |
| POST    | `/api/advertisements/{id}/applications` | public ou connecté   | Postuler à une annonce (voir ci-dessous)                                                                                                            |
| POST    | `/api/advertisements`                   | admin                | Création (`user_id` vaut par défaut l'admin courant)                                                                                                |
| PUT     | `/api/advertisements/{id}`              | admin                | Mise à jour                                                                                                                                         |
| DELETE  | `/api/advertisements/{id}`              | admin                | Suppression, avec ses candidatures                                                                                                                  |

Les annonces inactives ne sont visibles que par les admins (les autres reçoivent `404`).

**Candidature** : le corps est `{ "message": "...", "applicant_name": "...", "applicant_email": "...", "applicant_phone": "..." }`.
Un utilisateur connecté n'a besoin que de `message` : le nom et le téléphone sont repris de son profil et
l'email est toujours celui de son compte (un `applicant_email` envoyé est ignoré). Un visiteur anonyme doit
fournir les trois champs d'identité et ne peut pas utiliser l'email d'un compte existant (`409`, il doit se
connecter). Une candidature par email et par annonce, et une par utilisateur connecté et par annonce (`409`).
Quand `SMTP_HOST` est défini, le propriétaire de l'annonce (l'auteur, sinon l'entreprise) reçoit un email en
tâche de fond et `email_sent_at` est renseigné.

### Entreprises

| Méthode | Route                 | Accès  | Description                                           |
| ------- | --------------------- | ------ | ----------------------------------------------------- |
| GET     | `/api/companies`      | public | Liste ; filtre `q` (nom, ville)                       |
| GET     | `/api/companies/{id}` | public | Détail                                                |
| POST    | `/api/companies`      | admin  | Création                                              |
| PUT     | `/api/companies/{id}` | admin  | Mise à jour                                           |
| DELETE  | `/api/companies/{id}` | admin  | Suppression, avec ses annonces et leurs candidatures  |

### Utilisateurs (admin seulement)

| Méthode | Route             | Description                                                                              |
| ------- | ----------------- | ---------------------------------------------------------------------------------------- |
| GET     | `/api/users`      | Liste ; filtres `q` (nom d'utilisateur, prénom, nom, email), `role`, `company_id`        |
| GET     | `/api/users/{id}` | Détail                                                                                   |
| POST    | `/api/users`      | Création (tout rôle, `password` obligatoire, 8 à 72 caractères)                          |
| PUT     | `/api/users/{id}` | Mise à jour ; omettre `password` pour garder l'actuel                                    |
| DELETE  | `/api/users/{id}` | Suppression (un admin ne peut ni se supprimer ni retirer son propre rôle admin)          |

### Candidatures (admin seulement)

| Méthode | Route                    | Description                                                                 |
| ------- | ------------------------ | --------------------------------------------------------------------------- |
| GET     | `/api/applications`      | Liste ; filtres `q` (nom, email), `advertisement_id`, `user_id`, `status`   |
| GET     | `/api/applications/{id}` | Détail                                                                      |
| POST    | `/api/applications`      | Création                                                                    |
| PUT     | `/api/applications/{id}` | Mise à jour (par ex. changer le `status`)                                   |
| DELETE  | `/api/applications/{id}` | Suppression                                                                 |

## Pages

Les pages web (offres, authentification, administration) appartiennent au front, qui ne communique
qu'avec cette API. Ce backend ne sert aucun HTML.

| Page                    | Routes utilisées                                                                                                                 |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Offres                  | `GET /advertisements`, `GET /advertisements/{id}` (« En savoir plus »), `POST /advertisements/{id}/applications` (« Postuler ») |
| Connexion / inscription | `POST /auth/login`, `POST /auth/register`, `GET` et `PUT /auth/me`                                                               |
| Administration          | CRUD sur `/companies`, `/advertisements`, `/users`, `/applications` (listes paginées)                                            |
