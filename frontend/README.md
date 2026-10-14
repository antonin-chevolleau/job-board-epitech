# JobBoard | Frontend

Interface **React 19 + Vite + React Router**, en français. Elle ne parle qu'à l'API du
backend : le contrat d'API est décrit dans [`../backend/README.md`](../backend/README.md).

## Lancer en local

Prérequis : **Node.js 22.12+**, backend démarré (voir [`../README.md`](../README.md)).

```bash
npm install
cp .env.example .env   # seulement si vous n'avez pas déjà de .env
npm run dev
```

Ouvrir l'URL affichée par Vite (port 5173). Cette origine doit figurer dans
`CORS_ORIGINS` (`backend/.env`).

| Variable       | Description                                                                         |
| -------------- | ----------------------------------------------------------------------------------- |
| `VITE_API_URL` | URL du backend **sans** suffixe `/api` (défaut `http://127.0.0.1:8000`) ; le front ajoute `/api` |

## Scripts

```bash
npm run dev       # serveur de développement
npm run lint      # ESLint
npm run build     # build de production dans dist/
npm run preview   # sert le build
```

## Authentification

- `src/api.js` : client `fetch` commun. Il ajoute `Authorization: Bearer <token>` à chaque
  appel. Le jeton JWT est conservé dans `sessionStorage` (clé `jobboard-session`), donc par
  onglet. Sur une réponse `401`, il supprime le jeton et émet l'événement `session-expired`.
- `src/AuthProvider.jsx` : état du compte (`login`, `logout`, restauration via `GET /auth/me`).
  `useAuth()` (`src/auth.js`) y donne accès.
- `src/App.jsx` : routes ; `/Account` exige une connexion, `/Admin` le rôle `admin`.

## Structure

```bash
src/
|--- main.jsx, App.jsx # point d'entrée, routes
|--- api.js # client de l'API et jeton JWT
|--- AuthProvider.jsx, auth.js # session de l'utilisateur
|--- Header/ # en-tête et navigation
|--- Annonces/ # liste paginée et recherche (/, /Annonces)
|--- Advertisement/ # détail d'une annonce et candidature
|--- Login/ # connexion (/Login)
|--- Create_Account/ # inscription (/CreateAccount) et modification du profil (/Account)
|--- Admin/ # CRUD des ressources (/Admin) ; resources.js décrit les champs des formulaires
```
