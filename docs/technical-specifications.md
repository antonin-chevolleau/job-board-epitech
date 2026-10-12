# Spécifications techniques

## Back-end

### Base de données

- **MySQL** : système de gestion de base de données relationnelle en production
- **SQLite** : alternative SQL locale et base isolée pour les tests
- **SQLAlchemy** : ORM pour manipuler la base en Python
- **PyMySQL** : driver de connexion entre Python et MySQL
- **Sequel Ace** : client graphique pour consulter et administrer la base

### API

- **FastAPI** : framework web pour construire l'API
- **Pydantic** : validation et sérialisation des données
- **Authentification** : sessions opaques Bearer, expiration/révocation en base,
  hash des jetons SHA-256 et mots de passe PBKDF2-SHA256 salés
- **Initialisation** : `python -m app.seed`, sans suppression des tables existantes

### Outils de développement

- **Ruff** : linter et formateur de code Python
- **python-dotenv** : gestion des variables d'environnement via un fichier `.env`

### Déploiement

- **Render** : hébergement du back-end
- **Aiven** : hébergement de la BDD

## Front-end

### Interface

- **React** : bibliothèque pour construire l'interface utilisateur
- **React Router DOM** : gestion de la navigation entre les pages
- **CSS Modules** : styles CSS scopés par composant
- **fetch** : client commun `src/api.js`, URL configurable via `VITE_API_URL`
- **AuthProvider** : état du compte et jeton conservé par onglet (`sessionStorage`)

### Outils de développement

- **ESLint** : analyse statique et respect des conventions du code JavaScript
- **pytest / TestClient** : tests API sur SQLite en mémoire
- **Playwright Chromium** : parcours navigateur complet avec serveurs temporaires

### Déploiement

- **Vercel** : hébergement du front-end
