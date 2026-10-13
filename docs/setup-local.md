# Mise en place locale du projet JobBoard

Ce guide explique comment démarrer le projet après un `git pull`.

## Prérequis

- Python 3.12 ou plus récent
- Node.js + npm
- MySQL 8 en local
- Deux terminaux : un pour le backend, un pour le frontend

## 1. Récupérer le projet

```bash
git pull
```

Puis place-toi à la racine du projet :

```bash
cd job-board
```

## 2. Démarrer le backend

Dans un premier terminal :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # seulement si tu n'as pas déjà de .env
python -m uvicorn app.main:app --reload --port 8000
```

Avant la dernière commande :

1. crée la base locale et charge le schéma puis les données de démonstration
   (**attention** : `schemas.sql` supprime et recrée les tables) :

   ```bash
   mysql -u <user> -p -e "CREATE DATABASE job_board CHARACTER SET utf8mb4;"
   mysql -u <user> -p job_board < sql/schemas.sql
   mysql -u <user> -p job_board < sql/seed.sql
   ```

2. renseigne dans `backend/.env` :
   - `DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/job_board`
   - `SECRET_KEY` : `python3 -c "import secrets; print(secrets.token_hex(32))"`

Sans ces deux variables, le backend refuse de démarrer.

Le backend doit tourner sur :

```txt
http://127.0.0.1:8000
```

Pour vérifier :

```bash
curl http://127.0.0.1:8000/health
```

Résultat attendu :

```json
{"status":"ok"}
```

## 3. Démarrer le frontend

Dans un deuxième terminal, depuis la racine du projet :

```bash
cd frontend
npm install
npm run dev
```

Ouvre l'URL affichée par Vite (par défaut `http://localhost:5173`). Cette origine
doit figurer dans `CORS_ORIGINS` (`backend/.env`).

## 4. Comptes de démonstration

`sql/seed.sql` crée trois comptes, mot de passe `admin1234` :

| user_name   | rôle        |
| ----------- | ----------- |
| `admin`     | `admin`     |
| `recruiter` | `recruiter` |
| `jdoe`      | `user`      |

Connecte-toi avec le nom d'utilisateur (ou l'email) et le mot de passe.

## 5. Problèmes fréquents

### Le frontend affiche une erreur API

Vérifie que le backend tourne :

```bash
curl http://127.0.0.1:8000/health
```

Si ça ne répond pas, relance le backend.

### Le port 8000 est déjà utilisé

Lance le backend sur un autre port :

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Puis lance le frontend avec :

```bash
VITE_API_URL=http://127.0.0.1:8001 npm run dev
```

### Le port 5173 est déjà utilisé

Vite proposera souvent un autre port, par exemple `5174`.
Ouvre simplement l'URL affichée dans le terminal.

### Le backend refuse de démarrer

- `database_url Field required` : `DATABASE_URL` manque dans `backend/.env`.
- `SECRET_KEY must be at least 32 characters long` / `still the placeholder` :
  génère une vraie clé (voir plus haut).

### Le navigateur bloque les appels (CORS)

Ajoute l'origine exacte du front (ex. `http://localhost:5173`) à `CORS_ORIGINS`
dans `backend/.env`, puis relance le backend.

## 6. Tests utiles

Backend :

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

Les tests tournent sur la base du `.env`, seedée avec `sql/seed.sql`.

Frontend :

```bash
cd frontend
npm run lint
npm run build
```
