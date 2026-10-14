# Documentation du frontend

## 1. Vue d'ensemble

Le frontend est une application **React** construite avec **Vite**. Il fournit l'interface du job board :

- consultation et recherche d'offres ;
- affichage du détail d'une annonce ;
- candidature anonyme ou avec un compte ;
- création, connexion et modification d'un compte ;
- espace d'administration protégé ;
- gestion CRUD des annonces, entreprises, utilisateurs et candidatures.

Le frontend ne contient pas la logique métier principale et ne communique pas directement avec MySQL. Il appelle uniquement l'API REST FastAPI du dossier `backend/`.

### Technologies principales

| Technologie | Rôle |
| --- | --- |
| React | Composants, état local et cycle de vie de l'interface |
| React Router | Navigation entre les pages sans rechargement complet |
| Vite | Serveur de développement et build de production |
| `fetch` | Appels HTTP vers l'API backend |
| CSS Modules | Styles isolés pour certains composants |
| `sessionStorage` | Conservation temporaire du JWT de session |

Les dépendances sont déclarées dans `frontend/package.json`.

---

## 2. Démarrage de l'application

Le point d'entrée est `frontend/src/main.jsx`.

```jsx
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```

Les éléments sont imbriqués dans cet ordre :

1. `StrictMode` aide React à détecter certains problèmes pendant le développement.
2. `BrowserRouter` active les routes côté navigateur.
3. `App` contient la structure générale et les routes de l'application.

`frontend/index.html` fournit l'élément HTML `<div id="root">` dans lequel React monte l'application.

---

## 3. Organisation des fichiers

```text
frontend/
├── src/
│   ├── main.jsx                    # Point d'entrée React
│   ├── App.jsx                     # Routes et protections d'accès
│   ├── api.js                      # Client HTTP commun basé sur fetch
│   ├── auth.js                     # Contexte d'authentification
│   ├── AuthProvider.jsx            # État de session et login/logout
│   ├── Annonces/Annonces.jsx       # Liste, recherche et pagination
│   ├── Advertisement/Advertisement.jsx
│   │                                # Carte, détail et formulaire de candidature
│   ├── Login/Login.jsx             # Formulaire de connexion
│   ├── Create_Account/CreationAccount.jsx
│   │                                # Inscription et modification du compte
│   ├── Admin/Admin.jsx             # Interface d'administration
│   ├── Admin/resources.js          # Définition des ressources et champs CRUD
│   ├── Header/Header.jsx           # Navigation principale
│   ├── *.module.css                # Styles propres à certains composants
│   ├── App.css                     # Styles globaux de l'interface
│   └── index.css                   # Styles globaux minimaux
├── .env.example                    # Configuration de l'URL API
└── package.json                    # Scripts et dépendances
```

---

## 4. Routes frontend

Les routes sont déclarées dans `src/App.jsx`.

| Route | Composant | Accès | Fonction |
| --- | --- | --- | --- |
| `/` | redirection | public | Redirige vers `/Annonces` |
| `/Annonces` | `Annonces` | public | Liste, recherche et candidature |
| `/Login` | `Login` | public | Connexion |
| `/CreateAccount` | `CreateAccount` | public | Création d'un compte |
| `/Account` | `CreateAccount editing` | connecté | Modification des coordonnées |
| `/Admin` | `Admin` | administrateur | Gestion des ressources |
| autre route | message d'erreur | public | Page inexistante |

### Protection des routes

Le composant `Protected` vérifie trois cas :

1. pendant le chargement de la session, il affiche `Chargement de la session…` ;
2. sans utilisateur connecté, il redirige vers `/Login` ;
3. si `admin={true}` et que le rôle n'est pas `admin`, il redirige vers `/Annonces`.

La protection frontend améliore l'expérience utilisateur, mais la sécurité réelle est assurée par le backend. Un utilisateur pourrait contourner l'interface : l'API doit donc vérifier elle-même le JWT et le rôle.

---

## 5. Contexte d'authentification

### `AuthProvider.jsx`

`AuthProvider` centralise les informations de session :

```jsx
const [user, setUser] = useState(null)
const [loading, setLoading] = useState(true)
```

Il expose ensuite ces valeurs via `AuthContext` :

- `user` : profil courant ou `null` ;
- `loading` : indique si la session est encore vérifiée ;
- `login(credentials)` : connexion ;
- `logout()` : suppression locale de la session ;
- `setUser()` : mise à jour du profil en mémoire.

### Restauration de session

Au montage du provider, un appel `GET /api/auth/me` est effectué. Le token déjà présent dans `sessionStorage` est automatiquement ajouté par `api.js`.

- Si l'appel réussit, le profil est placé dans `user`.
- Si l'appel échoue, le token est supprimé.
- Un événement `session-expired` permet aux autres composants de remettre l'utilisateur à `null` après une réponse HTTP `401`.

### Connexion

La connexion se déroule en deux appels :

1. `POST /api/auth/login` avec un formulaire contenant `username` et `password` ;
2. conservation de `access_token` dans `sessionStorage` ;
3. `GET /api/auth/me` pour récupérer le profil complet.

Le rôle retourné permet ensuite de rediriger un administrateur vers `/Admin` et les autres utilisateurs vers `/Annonces`.

### Déconnexion

Il n'y a pas de route backend de déconnexion. Le frontend supprime simplement le JWT de `sessionStorage`, remet `user` à `null`, puis retourne vers `/Annonces`.

Le choix de `sessionStorage` signifie que le token est conservé pendant l'onglet ou la session du navigateur, mais pas comme une session persistante longue durée.

---

# 6. Le client API et `fetch`

Le fichier `src/api.js` contient la fonction commune `api()`. Tous les composants utilisent cette fonction au lieu d'appeler `fetch` directement.

Cette centralisation évite de répéter partout :

- la construction de l'URL ;
- l'ajout du token JWT ;
- la sérialisation des données ;
- la lecture des réponses JSON ;
- la gestion des erreurs HTTP ;
- la détection d'une session expirée.

## 6.1 Construction de l'URL

La base est construite ainsi :

```js
const baseUrl = `${(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')}/api`
```

La variable `VITE_API_URL` doit contenir l'origine du backend, **sans `/api`** :

```env
VITE_API_URL=http://127.0.0.1:8000
```

Si un composant appelle :

```js
api('/advertisements')
```

la requête envoyée devient :

```text
http://127.0.0.1:8000/api/advertisements
```

Le `replace(/\/$/, '')` supprime un éventuel slash final afin d'éviter une URL comme `/api//advertisements`.

## 6.2 Que fait `fetch` ?

`fetch` est une API JavaScript native qui envoie une requête HTTP et retourne une `Promise` contenant un objet `Response`.

Exemple simplifié :

```js
const response = await fetch(url, options)
const data = await response.json()
```

Le mot-clé `await` suspend la fonction `async` jusqu'à la réception de la réponse. Il ne bloque pas tout le navigateur : React peut continuer à afficher l'interface pendant que la requête réseau s'exécute.

Une réponse HTTP comporte notamment :

- `response.status` : code HTTP, par exemple `200`, `401` ou `404` ;
- `response.ok` : `true` pour les statuts `2xx`, sinon `false` ;
- `response.json()` : lecture du corps quand il est au format JSON.

Important : `fetch` ne rejette pas automatiquement la Promise pour un `404` ou un `500`. C'est pourquoi `api.js` teste explicitement `response.ok`.

## 6.3 Méthode HTTP et paramètres

La fonction reçoit un chemin et des options :

```js
api('/advertisements', {
  method: 'POST',
  body: { title: 'Développeur frontend' },
})
```

Les options sont transmises à `fetch` avec `...options`. Cela permet notamment de transmettre :

- `method` : `GET`, `POST`, `PUT` ou `DELETE` ;
- `signal` : signal d'annulation fourni par `AbortController` ;
- des headers supplémentaires.

### Corps JSON

Par défaut, un objet `body` est encodé en JSON :

```js
JSON.stringify(body)
```

et le header suivant est ajouté :

```http
Content-Type: application/json
```

C'est le format utilisé par l'inscription, la modification d'un profil et les opérations d'administration.

### Corps de formulaire

La connexion utilise un formulaire (`application/x-www-form-urlencoded`) car l'endpoint FastAPI de login attend les champs `username` et `password` sous cette forme :

```js
api('/auth/login', {
  method: 'POST',
  form: true,
  body: credentials,
})
```

`api.js` transforme alors l'objet avec :

```js
new URLSearchParams(body)
```

On obtient conceptuellement une requête contenant :

```text
username=admin&password=********
```

Le mot de passe n'est jamais écrit dans cette documentation et ne doit pas être ajouté aux logs.

## 6.4 JWT et header `Authorization`

Après une connexion réussie, le token est sauvegardé sous la clé `jobboard-session`.

À chaque appel suivant, `api.js` lit cette valeur et l'ajoute dans le header HTTP :

```http
Authorization: Bearer <token>
```

Le backend FastAPI peut alors identifier l'utilisateur et vérifier son rôle.

Les requêtes publiques fonctionnent sans token. Les routes protégées, comme `/auth/me`, `/users` ou `/applications`, nécessitent un token valide.

## 6.5 Gestion des réponses

`api.js` traite les réponses dans cet ordre :

1. si le statut est `204 No Content`, la fonction retourne `null` ;
2. sinon, elle tente de lire le JSON ;
3. si le statut n'est pas `2xx`, elle construit une `Error` ;
4. en cas de `401` alors qu'un token était présent, elle le supprime et déclenche `session-expired` ;
5. si tout va bien, elle retourne les données JSON au composant appelant.

Les erreurs FastAPI de validation peuvent contenir plusieurs détails. Le frontend les transforme en un message lisible sous la forme :

```text
nom_du_champ : message de validation
```

## 6.6 Erreur réseau et erreur HTTP

Il faut distinguer :

- **erreur réseau** : le backend est arrêté, l'URL est incorrecte ou le navigateur bloque la requête ;
- **erreur HTTP** : le backend a répondu avec `401`, `403`, `404`, `409`, `422` ou `500`.

Une erreur réseau affiche :

```text
API inaccessible. Vérifiez que le backend est démarré et que VITE_API_URL est correct.
```

Une erreur HTTP conserve le message fourni par l'API lorsqu'il existe.

## 6.7 Annulation d'une requête avec `AbortController`

Dans `Annonces.jsx` et `Admin.jsx`, un contrôleur est créé avant le fetch :

```js
const controller = new AbortController()
api('/advertisements', { signal: controller.signal })
```

Quand le composant est démonté ou que ses dépendances changent, l'effet retourne :

```js
return () => controller.abort()
```

Cela évite de laisser une ancienne requête modifier l'interface après une nouvelle recherche ou un changement de page. L'erreur `AbortError` est volontairement ignorée.

---

## 7. Page des annonces

`src/Annonces/Annonces.jsx` gère :

- la liste des annonces ;
- la recherche par mot-clé ;
- la recherche par lieu ;
- le filtre par type de contrat ;
- la pagination ;
- les états de chargement et d'erreur.

### Recherche différée

Les champs `query` et `location` représentent ce que l'utilisateur est en train de taper. Un `setTimeout` de 300 ms met à jour `search` après une courte pause.

Cette technique évite d'envoyer une requête à chaque frappe. Lorsque `search` change, l'effet recharge la liste.

### Pagination

Le frontend utilise une page commençant à `0` :

```js
page + 1
```

est envoyé à l'API, car le backend commence à `1`.

La requête ressemble à :

```text
GET /api/advertisements?page=1&limit=12&q=react&location=Paris&contract_type=CDI
```

L'API renvoie :

```json
{
  "items": [],
  "total": 42,
  "page": 1,
  "limit": 12
}
```

Le frontend place `items` dans `ads`, utilise `total` pour calculer le nombre de pages, puis rend une carte `Advertisement` par annonce.

---

## 8. Composant d'annonce et candidature

`src/Advertisement/Advertisement.jsx` reçoit une annonce via la prop `ad`.

Une annonce est affichée en deux niveaux :

1. **résumé** : titre, entreprise, date, contrat, lieu et description courte ;
2. **détail** : chargé uniquement lorsque l'utilisateur clique sur « En savoir plus ».

Le détail est récupéré avec :

```text
GET /api/advertisements/{id}
```

Le chargement à la demande évite de télécharger `full_description` pour toutes les annonces dès l'ouverture de la page.

### Candidature connectée

Si `user` existe :

- le frontend vérifie d'abord `/auth/me` pour détecter un token expiré ;
- il envoie le message à l'API ;
- le backend récupère l'identité depuis le compte connecté.

### Candidature anonyme

Sans compte, le formulaire demande :

- prénom ;
- nom ;
- email ;
- téléphone ;
- message.

Le prénom et le nom sont assemblés dans `applicant_name`, puis envoyés à :

```text
POST /api/advertisements/{id}/applications
```

Le backend applique les règles de sécurité et d'unicité, notamment l'interdiction pour un visiteur d'utiliser l'email d'un compte existant.

---

## 9. Inscription, connexion et compte

### Inscription

`CreateAccount` envoie les champs du formulaire à :

```text
POST /api/auth/register
```

Après la création, le frontend connecte automatiquement l'utilisateur avec `login()`, puis le redirige vers `/Annonces`.

### Modification du compte

Sur `/Account`, le même composant est rendu avec `editing={true}`. Dans ce mode, il envoie :

```text
PUT /api/auth/me
```

Le profil retourné remplace immédiatement l'ancien profil dans le contexte React.

### FormData

Les formulaires utilisent :

```js
Object.fromEntries(new FormData(event.currentTarget))
```

Cela transforme les champs HTML en objet JavaScript exploitable par `api()`.

---

## 10. Espace d'administration

`Admin.jsx` affiche quatre ressources :

- `advertisements` ;
- `companies` ;
- `users` ;
- `applications`.

La définition des champs est centralisée dans `Admin/resources.js`. Cette structure décrit pour chaque ressource :

- son libellé ;
- le texte du bouton de création ;
- les champs du formulaire ;
- le type HTML ;
- le caractère obligatoire ;
- la longueur maximale.

`ResourcePanel` est générique : le même composant peut afficher une liste, créer, modifier et supprimer les quatre types de ressources.

### Lecture

```text
GET /api/{resource}?page=1&limit=8
```

### Création

```text
POST /api/{resource}
```

### Modification

```text
PUT /api/{resource}/{id}
```

Le backend documente `PUT` comme un remplacement complet. Le formulaire doit donc fournir tous les champs attendus ; les champs optionnels vides sont convertis en `null`.

### Suppression

```text
DELETE /api/{resource}/{id}
```

Une suppression réussie retourne `204 No Content`, que `api()` convertit en `null`.

Les opérations d'administration sont protégées à deux niveaux :

- la route `/Admin` vérifie le rôle côté frontend ;
- l'API vérifie le JWT et le rôle `admin` côté backend.

---

## 11. Styles et responsive design

Les styles globaux se trouvent dans `App.css` et `index.css`.

- `index.css` initialise principalement le fond du document.
- `App.css` contient les couleurs, typographies, boutons, formulaires, cartes, tableaux, messages et media queries.
- `Header.module.css`, `Login.module.css`, `CreateAccount.module.css` et `Advertisement.module.css` isolent les styles des composants concernés.

Les media queries adaptent notamment :

- les colonnes en une seule colonne sur les petits écrans ;
- la navigation de l'administration ;
- les formulaires ;
- les tableaux avec défilement horizontal ;
- la grille des détails d'une annonce.

Les attributs ARIA (`role="status"`, `role="alert"`, `aria-expanded`, `aria-pressed`) permettent de mieux signaler les chargements, erreurs et contrôles interactifs aux technologies d'assistance.

---

## 12. Configuration et commandes

Depuis `frontend/` :

```bash
npm install
cp .env.example .env
npm run dev
```

Commandes disponibles :

```bash
npm run dev       # serveur Vite de développement
npm run lint      # vérification ESLint
npm run build     # build de production dans dist/
npm run preview   # prévisualisation du build
```

Le backend doit être lancé séparément sur `http://127.0.0.1:8000` ou sur l'URL indiquée par `VITE_API_URL`. L'origine du frontend doit aussi être autorisée dans `CORS_ORIGINS` côté backend.

---

## 13. Résumé du cycle complet d'une requête

Exemple : l'utilisateur recherche une annonce.

1. Il saisit un mot-clé dans `Annonces.jsx`.
2. Après 300 ms sans nouvelle frappe, l'état `search` est mis à jour.
3. Le `useEffect` construit les paramètres `page`, `limit`, `q`, `location` et `contract_type`.
4. `api()` construit l'URL complète sous `/api`.
5. `api()` récupère le JWT éventuel et prépare les headers.
6. `fetch()` envoie la requête HTTP.
7. Le backend filtre les annonces et renvoie du JSON paginé.
8. `api()` vérifie le statut HTTP et retourne les données.
9. `Annonces.jsx` met à jour `ads` et `total`.
10. React rerend les composants `Advertisement`.

Ce découpage permet de séparer clairement :

- l'affichage et les interactions dans les composants React ;
- la communication HTTP dans `api.js` ;
- l'authentification de session dans `AuthProvider.jsx` ;
- la logique métier et les autorisations dans le backend FastAPI.
