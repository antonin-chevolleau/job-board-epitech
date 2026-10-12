# JobBoard — Epitech

Job board React + FastAPI + SQLAlchemy, construit à partir du code existant.
Le périmètre final suit `sujets/jobBoard-project.pdf` ; le bootstrap sert de guide
pour le modèle SQL, les routes REST et les appels asynchrones.

## Lancer en local

Prérequis : **Python 3.12+**, **Node.js 22.12+**, npm.
Deux terminaux sont nécessaires. Les commandes suivantes utilisent SQLite, une
base SQL locale ; aucun accès à Aiven n'est nécessaire.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # seulement si vous n'avez pas déjà de .env
python -m app.seed --demo --admin-email admin@example.com
# Un mot de passe de 10 à 128 caractères est demandé, sans affichage.
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API : <http://127.0.0.1:8000>
- Swagger / contrats JSON : <http://127.0.0.1:8000/docs>
- Santé : <http://127.0.0.1:8000/health>
- `app.seed` crée les tables absentes sans supprimer les tables existantes.
- `--demo` ajoute deux entreprises et quatre annonces si la table des entreprises
  est vide. Les données sont créées **via le backend**, pas par le navigateur.
- `--admin-email` crée un nouveau compte admin ; une adresse existante est refusée.
  Aucun mot de passe admin par défaut n'est livré.
- Pour simplement créer les tables : `python -m app.seed`.

### 2. Frontend

```bash
cd frontend
npm ci
cp .env.example .env  # seulement si vous n'avez pas déjà de .env
npm run dev -- --host 127.0.0.1 --port 5173
```

Ouvrir <http://127.0.0.1:5173>. `VITE_API_URL` doit pointer vers le backend,
sans suffixe `/api` (par défaut `http://127.0.0.1:8000`). Redémarrer Vite après
modification du `.env`. Les variables `VITE_*` sont publiques : jamais de secret.

### MySQL / Aiven

La connexion MySQL existante reste prise en charge. Dans `backend/.env` :

```dotenv
DATABASE_URL=mysql+pymysql://user:password@host:port/dbname
CA_CERT_PATH=certs/ca.pem
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
SESSION_HOURS=12
```

Encoder les caractères spéciaux du mot de passe dans l'URL. Pour un MySQL local
sans TLS, laisser `CA_CERT_PATH` vide. Sauvegarder la base avant toute mise à jour.
`python -m app.seed` ajoute notamment les tables `credentials` et `auth_sessions` ;
il ne migre pas les colonnes existantes et n'attribue pas de mot de passe aux
anciennes personnes. Les quatre tables métier existantes sont conservées.
Les tests fournis **n'utilisent jamais la base distante**. La connexion Aiven doit
être vérifiée séparément dans votre environnement.

## Pages et parcours

| URL | Fonction |
| --- | --- |
| `/`, `/Annonces` | Liste paginée, détails chargés à la demande dans la carte, candidature |
| `/CreateAccount` | Inscription puis connexion automatique |
| `/Login` | Connexion ; admin → `/Admin`, utilisateur → `/Annonces` |
| `/Account` | Coordonnées personnelles modifiables, connexion requise |
| `/Admin` | CRUD paginé des annonces, entreprises, personnes et candidatures |

Les données dynamiques proviennent de l'API. Le fichier mock préexistant n'est pas
utilisé. Les détails s'ouvrent **sans navigation, popup ni rechargement**.
Les candidatures connectées utilisent les coordonnées du compte côté serveur ;
aucun ID de candidat fourni par le navigateur n'est accepté. Une confirmation
n'est affichée qu'après l'enregistrement effectif en base.

## Modèle SQL

- `companies` → plusieurs `advertisements`.
- `people` ↔ `advertisements` via `applications` (message, statut, dates).
- `credentials` : hash PBKDF2-SHA256 salé du mot de passe, lié à une personne.
- `auth_sessions` : hash du jeton de session et expiration, lié à une personne.
- Suppression d'une entreprise → ses annonces et leurs candidatures ; suppression
  d'une personne → ses candidatures, identifiants et sessions.
- Les dates enregistrées par le backend sont en UTC.

Détails : [`docs/data-models.md`](docs/data-models.md).
Le projet final n'exige pas les catégories propres à l'exemple HireLoop du bootstrap.
Des requêtes de travail SQL sont fournies dans
[`docs/bootstrap-queries.sql`](docs/bootstrap-queries.sql).

## API

Les collections utilisent `offset=0&limit=20` (`limit` entre 1 et 100).

| Routes | Accès |
| --- | --- |
| `GET /advertisements/`, `GET /advertisements/{id}` | Public : annonces publiées ; admin : tous les statuts |
| `POST /advertisements/`, `PATCH/DELETE /advertisements/{id}` | Admin |
| `GET /companies/{id}/ads` | Annonces publiées d'une entreprise (tous statuts pour l'admin) |
| `POST /advertisements/{id}/applications` | Candidature visiteur ou connecté |
| `GET/POST /companies/`, `GET/PATCH/DELETE /companies/{id}` | Admin |
| `GET/POST /people/`, `GET/PATCH/DELETE /people/{id}` | Admin |
| `GET/POST /applications/`, `GET/PATCH/DELETE /applications/{id}` | Admin |
| `POST /auth/register`, `POST /auth/login` | Public |
| `GET/PATCH /auth/me`, `POST /auth/logout` | Connecté |

`/advertisements` est l'équivalent de `/ads` du bootstrap, pour conserver le contrat
et les modèles du backend existant. Les listes sont des tableaux JSON.
Codes : `200`, `201` création, `204` suppression/déconnexion, `400` champ obligatoire
manquant, `401` non connecté/session expirée, `403` non-admin, `404` absent,
`409` conflit, `422` valeur invalide. Les schémas précis sont disponibles dans Swagger.

Candidature visiteur :

```bash
curl -X POST http://127.0.0.1:8000/advertisements/1/applications \
  -H 'Content-Type: application/json' \
  -d '{"firstname":"Ada","lastname":"Lovelace","email":"ada@example.com","phone":"0600000000","message":"Je souhaite rejoindre votre équipe."}'
```

Candidature connectée : même route, `Authorization: Bearer <access_token>`,
corps `{"message":"Je souhaite rejoindre votre équipe."}`.

### Authentification et limites explicites

- Sessions opaques expirant après 12 h par défaut, révoquées à la déconnexion.
  Le navigateur garde le jeton dans `sessionStorage` (par onglet) ; la base ne garde
  que son hash. Les mots de passe et hashes ne sont jamais renvoyés par l'API.
- Autorisations contrôlées **dans l'API**, en plus des protections React.
  L'inscription et la modification de compte ne permettent pas de devenir admin.
- Une candidature anonyme ne peut pas être rattachée à une adresse déjà présente
  en base : ce serait permettre d'usurper l'identité d'un autre candidat.
  Créez un compte **avant** de postuler pour utiliser la même adresse sur plusieurs
  offres. Une fiche visiteur existante nécessite une intervention administrateur
  avant inscription ; la vérification d'email/récupération de compte reste à ajouter.
- Les personnes créées depuis l'administration sont des fiches, pas des comptes
  de connexion. La création d'un compte passe par l'inscription ou le seed admin.
- Les messages sont stockés dans les candidatures, **aucun email réel n'est envoyé**.
- Avant exposition publique : HTTPS, limitation des tentatives de connexion,
  vérification d'email/récupération de mot de passe, politique de sauvegarde et
  revue de sécurité. Cette livraison est validée localement, pas déployée.

## Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
ruff check .
ruff format --check .
```

Tests API avec une base SQLite jetable : CRUD, validation, publication des annonces,
inscription, sessions, permissions, candidatures, cascade et pagination.

```bash
cd frontend
npm run lint
npm run build
```

Parcours navigateur automatisé (depuis `backend`, npm installé dans `frontend`) :

```bash
python -m playwright install chromium
# Sous Linux, si des bibliothèques système manquent :
# python -m playwright install-deps chromium
python tests/browser_smoke.py
```

Ce test lance temporairement l'API sur `18000` et Vite sur `15173`, crée sa propre
base et arrête ses serveurs en fin d'exécution. Il couvre les détails, candidature
visiteur, inscription, candidature connectée, modification du profil, accès admin,
CRUD et affichage mobile. Aucun compte de test n'est ajouté à votre base habituelle.

## Production

`npm run build` génère `frontend/dist`. Configurer le serveur de fichiers pour
rediriger les routes React vers `index.html`. Définir `VITE_API_URL` **au build**
et les origines autorisées exactes dans `CORS_ORIGINS`. Démarrer FastAPI avec
`uvicorn main:app --host 0.0.0.0 --port 8000` depuis `backend` et utiliser MySQL.
Ne pas utiliser `--reload` en production et ne jamais versionner les fichiers `.env`.
