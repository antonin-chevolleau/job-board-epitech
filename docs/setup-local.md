# Mise en place locale du projet JobBoard

Ce guide explique comment démarrer le projet après un `git pull`.

## Prérequis

- Python 3.12 ou plus récent
- Node.js + npm
- Deux terminaux : un pour le backend, un pour le frontend

## 1. Récupérer le projet

```bash
git pull
```

Puis place-toi à la racine du projet :

```bash
cd ~/ecole/job-board-bootstrap
```

## 2. Démarrer le backend

Dans un premier terminal :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed --demo
python -m uvicorn main:app --reload --port 8000
```

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
VITE_API_URL=http://127.0.0.1:8000 npm run dev
```

Le frontend doit tourner sur :

```txt
http://127.0.0.1:5173
```

## 4. Compte admin local

Si aucun compte admin n'existe, crée-en un :

```bash
cd backend
source .venv/bin/activate
python -m app.seed --admin-email admin@example.com
```

Un mot de passe sera demandé.

Dans l'interface, connecte-toi avec :

```txt
email: admin@example.com
password: le mot de passe choisi
```

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
python -m uvicorn main:app --reload --port 8001
```

Puis lance le frontend avec :

```bash
VITE_API_URL=http://127.0.0.1:8001 npm run dev
```

### Le port 5173 est déjà utilisé

Vite proposera souvent un autre port, par exemple `5174`.
Ouvre simplement l'URL affichée dans le terminal.

### Réinitialiser les données locales

Si tu utilises SQLite localement :

```bash
cd backend
rm -f jobboard.db
source .venv/bin/activate
python -m app.seed --demo
```

Puis relance le backend.

## 6. Tests utiles

Backend :

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

Frontend :

```bash
cd frontend
npm run lint
npm run build
```
