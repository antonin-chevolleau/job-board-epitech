# Spécifications techniques

Le projet tourne entièrement en local.

## Back-end

### Base de données

- **MySQL 8** : seule base de l'application (et des tests)
- **SQL brut** : `backend/sql/schemas.sql` (schéma de référence, supprime et recrée les tables)
  et `backend/sql/seed.sql` (données de démonstration)
- **SQLAlchemy 2** : ORM, modèles miroirs du schéma SQL
- **PyMySQL** : driver de connexion entre Python et MySQL

### API

- **FastAPI** : framework web, routes sous `/api`, Swagger sur `/docs`
- **Pydantic / pydantic-settings** : validation des données et configuration via `.env`
- **Authentification** : JWT Bearer (PyJWT, HS256, 60 min par défaut), mots de passe **bcrypt**
- **Rôles** : `user`, `recruiter`, `admin` ; contrôle des droits côté serveur
- **Limitation de débit** : fenêtre glissante en mémoire, par IP (login, candidature)
- **Email** : notification SMTP optionnelle au propriétaire de l'annonce, en tâche de fond

### Outils de développement

- **pytest / TestClient** : tests API sur la base MySQL du `.env` (seedée)

## Front-end

- **React 19** + **Vite**
- **React Router DOM** : navigation entre les pages
- **CSS Modules** + `App.css` : styles
- **fetch** : client commun `src/api.js` (préfixe `/api`, URL via `VITE_API_URL`)
- **AuthProvider** : état du compte, jeton JWT conservé par onglet (`sessionStorage`)
- **ESLint** : analyse statique
- Interface en français
