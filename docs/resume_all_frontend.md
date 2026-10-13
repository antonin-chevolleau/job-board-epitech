# Résumé complet du frontend

Ce document recense les fichiers du dossier `frontend/` et explique le rôle de chaque composant, module, configuration et feuille de style.

Le frontend est une application React/Vite. Il communique avec le backend FastAPI à travers `src/api.js` et ne se connecte jamais directement à MySQL.

---

## 1. Vue globale de l'architecture

```text
index.html
└── src/main.jsx
    ├── BrowserRouter
    └── App.jsx
        ├── AuthProvider.jsx
        │   └── AuthContext / session utilisateur
        ├── Header.jsx
        └── Routes
            ├── Annonces.jsx
            │   └── Advertisement.jsx
            │       └── ApplicationForm
            ├── Login.jsx
            ├── CreationAccount.jsx
            └── Admin.jsx
                └── ResourcePanel
                    └── ResourceForm
```

Le flux général est le suivant :

1. `index.html` fournit le conteneur HTML `#root`.
2. `main.jsx` démarre React et active le routeur.
3. `App.jsx` construit la structure de l'application et les routes.
4. `AuthProvider.jsx` vérifie la session et fournit l'utilisateur courant.
5. Les composants de page utilisent `api.js` pour appeler le backend.
6. React met à jour l'interface avec les données reçues.

---

## 2. Inventaire des fichiers

### Fichiers racine de `frontend/`

| Fichier | Rôle |
| --- | --- |
| `index.html` | Document HTML de départ |
| `package.json` | Dépendances et scripts npm |
| `package-lock.json` | Versions exactes installées par npm |
| `vite.config.js` | Configuration Vite |
| `eslint.config.js` | Configuration ESLint |
| `.env.example` | Exemple de configuration de l'API |
| `.gitignore` | Fichiers exclus de Git |
| `README.md` | Documentation minimale actuelle |

### Fichiers React et JavaScript

| Fichier | Rôle |
| --- | --- |
| `src/main.jsx` | Point d'entrée React |
| `src/App.jsx` | Routes et protection des pages |
| `src/api.js` | Client HTTP commun basé sur `fetch` |
| `src/auth.js` | Contexte et hook d'authentification |
| `src/AuthProvider.jsx` | Gestion de la session utilisateur |
| `src/Annonces/Annonces.jsx` | Liste, recherche et pagination des offres |
| `src/Advertisement/Advertisement.jsx` | Carte, détail et candidature à une offre |
| `src/Login/Login.jsx` | Connexion |
| `src/Create_Account/CreationAccount.jsx` | Inscription et modification du compte |
| `src/Header/Header.jsx` | Navigation principale |
| `src/Admin/Admin.jsx` | Espace d'administration |
| `src/Admin/resources.js` | Définition des ressources administrables |

### Styles et ressources

| Fichier | Rôle |
| --- | --- |
| `src/index.css` | Initialisation globale du document |
| `src/App.css` | Design global et responsive design |
| `src/Header/Header.module.css` | Style isolé du header |
| `src/Advertisement/Advertisement.module.css` | Style isolé des cartes d'annonces |
| `src/Login/Login.module.css` | Ancienne feuille de styles de connexion |
| `src/Create_Account/CreateAccount.module.css` | Ancienne feuille de styles de compte |
| `public/images/home_icon.png` | Image publique disponible par URL statique |

---

# 3. Fichiers de démarrage et de configuration

## 3.1 `index.html`

`index.html` est le document chargé par le navigateur.

Éléments importants :

```html
<html lang="fr">
```

L'attribut `lang="fr"` indique que l'interface est en français, ce qui aide les lecteurs d'écran et les moteurs de recherche.

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

Cette balise rend la mise en page adaptée aux écrans mobiles.

```html
<div id="root"></div>
<script type="module" src="/src/main.jsx"></script>
```

React ne remplace pas toute la page HTML. Il monte l'application dans le `<div id="root">`. Le script charge ensuite le point d'entrée JavaScript.

Le titre et la description sont également définis ici :

```html
<title>JobBoard — Offres d’emploi</title>
<meta name="description" content="Découvrez les offres d’emploi et postulez avec JobBoard." />
```

---

## 3.2 `src/main.jsx`

C'est le point d'entrée de React.

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
```

Le fichier importe :

- `StrictMode` pour détecter certains problèmes en développement ;
- `createRoot` pour créer la racine React moderne ;
- `BrowserRouter` pour gérer les URLs côté navigateur ;
- les styles globaux ;
- le composant principal `App`.

Le rendu est imbriqué ainsi :

```jsx
<StrictMode>
  <BrowserRouter>
    <App />
  </BrowserRouter>
</StrictMode>
```

`BrowserRouter` permet d'utiliser `Routes`, `Route`, `Link`, `Navigate` et `useNavigate` dans les autres composants.

---

## 3.3 `package.json`

Ce fichier décrit le projet npm.

### Scripts

```json
"dev": "vite"
```

Démarre le serveur de développement Vite.

```json
"build": "vite build"
```

Compile l'application optimisée dans `dist/`.

```json
"lint": "eslint ."
```

Analyse les fichiers JavaScript et JSX avec ESLint.

```json
"preview": "vite preview"
```

Sert localement le build déjà généré.

### Dépendances principales

- `react` : bibliothèque d'interface ;
- `react-dom` : rendu React dans le navigateur ;
- `react-router-dom` : routage ;
- `vite` : serveur et outil de compilation ;
- `eslint` : analyse statique ;
- `eslint-plugin-react-hooks` : vérification des règles des hooks ;
- `eslint-plugin-react-refresh` : compatibilité avec le rechargement rapide Vite.

---

## 3.4 `package-lock.json`

`package-lock.json` est généré par npm. Il conserve les versions exactes des dépendances directes et indirectes.

Son objectif est de garantir que deux installations du projet utilisent une arborescence de packages identique, ou aussi proche que possible.

Il ne doit généralement pas être modifié manuellement. Il est mis à jour avec :

```bash
npm install
```

---

## 3.5 `vite.config.js`

```js
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
})
```

La configuration active le plugin React de Vite. Ce plugin permet notamment :

- la transformation du JSX ;
- le Fast Refresh pendant le développement ;
- l'intégration correcte de React avec Vite.

Le projet n'a pas de proxy Vite spécifique : l'URL du backend est donc construite directement à partir de `VITE_API_URL`.

---

## 3.6 `eslint.config.js`

La configuration ESLint utilise le nouveau format `defineConfig`.

Elle active :

- les règles JavaScript recommandées ;
- les règles des hooks React ;
- les règles React Refresh de Vite ;
- les globals du navigateur ;
- l'analyse du JSX dans les fichiers `.jsx`.

```js
globalIgnores(['dist'])
```

Le dossier de build n'est pas analysé.

```js
files: ['**/*.{js,jsx}']
```

ESLint s'applique aux fichiers JavaScript et JSX.

Cette configuration aide à détecter les erreurs comme :

- un hook appelé au mauvais endroit ;
- une dépendance manquante dans un `useEffect` ;
- une variable non utilisée ;
- un problème de compatibilité avec React Refresh.

---

## 3.7 `.env.example`

```env
VITE_API_URL=http://127.0.0.1:8000
```

Cette variable correspond à l'origine du backend, sans le suffixe `/api`.

Le fichier `api.js` ajoute lui-même `/api`. La valeur suivante est donc correcte :

```env
VITE_API_URL=http://127.0.0.1:8000
```

et non :

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Sinon le frontend construirait une URL incorrecte contenant `/api/api`.

Les fichiers `.env` réels sont ignorés par Git afin de ne pas versionner de configuration locale ou de secrets.

---

## 3.8 `.gitignore`

Le fichier exclut notamment :

- `node_modules/` : dépendances installées ;
- `dist/` : fichiers générés par le build ;
- `.vite/` : cache Vite ;
- `.env` et les fichiers `.env.*` sauf `.env.example` ;
- logs npm ;
- fichiers d'IDE comme `.vscode/` et `.idea/`.

Le fichier `.env.example` est explicitement conservé dans Git pour documenter la configuration attendue.

---

## 3.9 `frontend/README.md`

Le README actuel contient une description minimale du frontend. La documentation détaillée se trouve dans :

- `docs/frontend.md` : explication de l'architecture et de `fetch` ;
- `docs/resume_all_frontend.md` : inventaire détaillé de tous les fichiers et composants.

---

# 4. Composants principaux

## 4.1 `src/App.jsx`

`App` est le composant racine de l'interface.

Il importe :

```jsx
import { Navigate, Routes, Route } from 'react-router-dom'
```

- `Routes` contient les routes ;
- `Route` associe une URL à un composant ;
- `Navigate` effectue une redirection.

Il importe également le header, les pages et `AuthProvider`.

### Composant `Protected`

`Protected` est un composant interne utilisé pour les pages nécessitant une connexion.

```jsx
function Protected({ children, admin = false }) {
  const { user, loading } = useAuth()
```

Il récupère l'état de session depuis le contexte.

#### Cas 1 : session en cours de vérification

```jsx
if (loading) return <p role="status">Chargement de la session…</p>
```

La page n'est pas immédiatement redirigée afin d'éviter qu'un utilisateur déjà connecté soit envoyé par erreur vers la page de login pendant le chargement.

#### Cas 2 : utilisateur absent

```jsx
if (!user) return <Navigate to="/Login" replace />
```

La navigation remplace l'entrée courante de l'historique grâce à `replace`.

#### Cas 3 : rôle insuffisant

```jsx
if (admin && user.role !== 'admin') return <Navigate to="/Annonces" replace />
```

Une page administrative n'est rendue que pour un utilisateur dont le rôle vaut `admin`.

### Structure de `App`

`App` enveloppe l'application dans `AuthProvider`, puis affiche :

1. `Header` ;
2. les routes dans `<main>` ;
3. le footer.

### Routes

- `/` redirige vers `/Annonces` ;
- `/CreateAccount` affiche le formulaire d'inscription ;
- `/Login` affiche la connexion ;
- `/Annonces` affiche les offres ;
- `/Account` utilise `CreateAccount` en mode édition et est protégé ;
- `/Admin` affiche l'administration et exige le rôle admin ;
- `*` affiche une page inexistante.

`App` ne contient pas les appels API métier. Il orchestre la navigation et les protections.

---

## 4.2 `src/auth.js`

Ce fichier contient le contexte et le hook d'authentification.

```jsx
export const AuthContext = createContext(null)
```

`AuthContext` est le canal par lequel `AuthProvider` transmet les données de session aux composants descendants.

```jsx
export function useAuth() {
  return useContext(AuthContext)
}
```

`useAuth()` simplifie l'accès au contexte : les composants peuvent écrire `const { user } = useAuth()` au lieu d'appeler directement `useContext(AuthContext)`.

Ce fichier ne contient pas la logique de connexion. Cette logique se trouve dans `AuthProvider.jsx`.

---

## 4.3 `src/AuthProvider.jsx`

`AuthProvider` possède l'état global de session.

### États

```jsx
const [user, setUser] = useState(null)
const [loading, setLoading] = useState(true)
```

- `user` contient le profil connecté ;
- `loading` empêche l'interface de décider trop tôt que l'utilisateur est anonyme.

### Vérification initiale

Le `useEffect` exécuté au montage appelle :

```text
GET /api/auth/me
```

Si le token présent dans `sessionStorage` est valide, l'API retourne le profil et celui-ci est enregistré avec `setUser`.

Si l'appel échoue, `setToken(null)` supprime le token local.

### Événement `session-expired`

`api.js` déclenche cet événement lorsqu'une requête authentifiée reçoit `401`.

`AuthProvider` écoute l'événement :

```jsx
const expire = () => setUser(null)
window.addEventListener('session-expired', expire)
```

Le profil est alors vidé dans toute l'application.

Le nettoyage de l'écouteur est réalisé au démontage du provider.

### Fonction `login`

```jsx
async function login(credentials) {
  const result = await api('/auth/login', {
    method: 'POST',
    form: true,
    body: credentials,
  })
  setToken(result.access_token)
  const person = await api('/auth/me')
  setUser(person)
  return person
}
```

Le flux est :

1. envoi du nom d'utilisateur/email et du mot de passe ;
2. réception du JWT ;
3. stockage du JWT ;
4. récupération du profil complet ;
5. mise à jour de `user` ;
6. retour du profil au composant appelant.

### Fonction `logout`

```jsx
function logout() {
  setToken(null)
  setUser(null)
}
```

La déconnexion est locale : elle retire le token et le profil.

### Valeur fournie

```jsx
<AuthContext.Provider value={{ user, loading, login, logout, setUser }}>
```

Tous les composants descendants peuvent récupérer ces cinq valeurs grâce à `useAuth()`.

---

## 4.4 `src/Header/Header.jsx`

`Header` affiche la navigation en fonction de l'état de connexion.

### Navigation publique

Quand `user` est absent, le header affiche :

- le lien vers les offres ;
- le lien « Se connecter » ;
- le lien « Créer un compte ».

### Navigation connectée

Quand `user` existe, il affiche :

- les offres ;
- le compte ;
- le lien Admin uniquement si `user.role === 'admin'` ;
- le bouton de déconnexion.

### Déconnexion

```jsx
function disconnect() {
  logout()
  navigate('/Annonces')
}
```

Le contexte est vidé puis la navigation retourne vers les annonces.

### CSS Module

Le composant importe :

```jsx
import style from './Header.module.css'
```

Les classes comme `style.header`, `style.brand` et `style.nav` sont transformées par Vite en noms de classes isolés pour éviter les collisions CSS.

---

## 4.5 `src/Annonces/Annonces.jsx`

`Annonces` est la page principale du job board.

Elle gère :

- les offres reçues de l'API ;
- le chargement ;
- les erreurs ;
- la recherche ;
- les filtres ;
- la pagination ;
- la relance d'une requête.

### Constantes

```jsx
const pageSize = 12
const contractTypes = ['CDI', 'CDD', 'Stage', 'Alternance', 'Freelance']
```

La page demande 12 offres à la fois et propose cinq types de contrat.

### États

- `ads` : offres affichées ;
- `total` : nombre total d'offres correspondant aux filtres ;
- `loading` : requête en cours ;
- `error` : message d'erreur ;
- `page` : page frontend commençant à zéro ;
- `retry` : compteur utilisé pour forcer un nouveau chargement ;
- `query` : texte actuellement saisi ;
- `location` : lieu actuellement saisi ;
- `contract` : contrat sélectionné ;
- `search` : critères réellement appliqués à l'API.

### Différence entre `query` et `search`

`query` change à chaque frappe. `search` ne change qu'après 300 ms sans nouvelle frappe.

```jsx
const timer = setTimeout(() => {
  const next = { q: query.trim(), location: location.trim() }
  setSearch(next)
  setPage(0)
}, 300)
```

Cette temporisation évite une requête réseau à chaque caractère.

### Chargement des offres

L'effet de chargement est déclenché lorsque changent :

- la page ;
- le compteur `retry` ;
- la recherche ;
- le type de contrat ;
- l'utilisateur ;
- l'état de chargement de la session.

La requête est construite avec `URLSearchParams` :

```text
GET /api/advertisements?page=1&limit=12&q=...&location=...&contract_type=...
```

Le frontend utilise `page + 1` car son index commence à zéro tandis que l'API commence à un.

### Annulation

Un `AbortController` annule la requête précédente quand l'effet est nettoyé. Cela évite les réponses obsolètes et les mises à jour après démontage.

### Rendu

Les états affichés sont :

1. chargement ;
2. erreur avec bouton « Réessayer » ;
3. message lorsqu'aucune offre ne correspond ;
4. liste de composants `Advertisement`.

### Pagination

Le nombre de pages est calculé ainsi :

```jsx
Math.max(1, Math.ceil(total / pageSize))
```

Les boutons sont désactivés :

- « Précédent » sur la première page ;
- « Suivant » sur la dernière page ;
- pendant un chargement ;
- lorsque la requête est en erreur pour « Suivant ».

---

## 4.6 `src/Advertisement/Advertisement.jsx`

Ce fichier contient deux composants :

- `Advertisement` : carte d'une offre ;
- `ApplicationForm` : formulaire de candidature.

### Fonction `formatSalary`

Cette fonction affiche un salaire lisible :

- `null` ou `undefined` devient « Non précisé » ;
- un nombre est formaté selon la locale française ;
- le symbole `€` est ajouté.

### Composant `Advertisement`

Il reçoit une annonce par la prop `ad`.

#### États

- `details` : contenu détaillé reçu de l'API ;
- `expanded` : indique si le détail est visible ;
- `applying` : indique si le formulaire de candidature est ouvert ;
- `busy` : indique si le détail est en cours de chargement ;
- `error` : erreur de récupération du détail.

#### Résumé affiché

La carte montre :

- l'initiale de l'entreprise ;
- le titre ;
- le nom de l'entreprise ;
- la date de création ;
- le type de contrat ;
- le lieu ;
- le temps de travail lorsqu'il existe ;
- la description courte.

#### Détail à la demande

Au clic sur « En savoir plus », le composant appelle :

```text
GET /api/advertisements/{id}
```

Le détail contient notamment :

- `full_description` ;
- le salaire ;
- le lieu ;
- le temps de travail ;
- le contrat.

Le composant repasse à l'état fermé si l'utilisateur clique sur « Voir moins ».

#### Candidature

Le bouton « Postuler » ouvre ou ferme `ApplicationForm`. Il est désactivé pour une annonce inactive.

### Composant `ApplicationForm`

Le formulaire utilise `FormData` pour récupérer les champs :

```jsx
const body = Object.fromEntries(new FormData(event.currentTarget))
```

#### Visiteur anonyme

Le formulaire demande prénom, nom, email, téléphone et message.

Le prénom et le nom sont combinés :

```jsx
body.applicant_name = `${body.first_name} ${body.last_name}`
```

Les propriétés temporaires `first_name` et `last_name` sont ensuite supprimées.

#### Utilisateur connecté

Le formulaire affiche les coordonnées connues du compte et ne demande que le message.

Avant de postuler, le composant vérifie `/auth/me`. Cela permet de détecter rapidement un token expiré.

#### Envoi

La candidature est envoyée avec :

```text
POST /api/advertisements/{id}/applications
```

En cas de succès, le formulaire est remplacé par un message de confirmation.

En cas d'erreur `401` pour un utilisateur connecté, le composant redirige vers `/Login`.

### CSS Module

`Advertisement.module.css` contient les styles propres aux cartes :

- `.card` : grille principale ;
- `.initial` : cercle contenant l'initiale ;
- `.content` : contenu flexible ;
- `.meta` : entreprise et date ;
- `.job_title` : titre du poste ;
- `.badges` : badges de contrat et lieu ;
- `.buttons` : actions ;
- `.detailGrid` : disposition du détail.

À moins de 720 pixels, la carte et la grille du détail passent sur une seule colonne.

---

## 4.7 `src/Login/Login.jsx`

`Login` affiche le formulaire de connexion.

### États

- `error` : message d'erreur ;
- `busy` : empêche plusieurs soumissions simultanées.

### Soumission

Le formulaire est converti en objet avec `FormData`, puis envoyé à `login()` fourni par `AuthProvider`.

```jsx
const user = await login(body)
navigate(user.role === 'admin' ? '/Admin' : '/Annonces')
```

La destination dépend du rôle reçu après connexion.

### Champs

- `username` : nom d'utilisateur ou email ;
- `password` : mot de passe.

Les attributs `autoComplete` facilitent l'utilisation avec un gestionnaire de mots de passe.

### Erreurs

Si la connexion échoue, l'erreur normalisée par `api.js` est affichée dans un élément `role="alert"`.

### Navigation secondaire

Un lien permet d'aller vers `/CreateAccount`.

---

## 4.8 `src/Create_Account/CreationAccount.jsx`

Le composant `CreateAccount` possède deux modes :

- inscription avec `editing={false}` ;
- modification du compte avec `editing={true}`.

### États

- `error` : erreur retournée par l'API ;
- `success` : message de réussite ;
- `busy` : soumission en cours.

### Mode inscription

Le formulaire collecte :

- nom d'utilisateur ;
- prénom ;
- nom ;
- email ;
- téléphone ;
- mot de passe ;
- consentement à la conservation des coordonnées.

La requête est :

```text
POST /api/auth/register
```

Après l'inscription, le composant appelle immédiatement `login()` avec le nom d'utilisateur et le mot de passe, puis redirige vers `/Annonces`.

### Mode modification

Quand `editing` vaut `true`, le composant affiche les valeurs présentes dans `user` et envoie :

```text
PUT /api/auth/me
```

Le profil retourné est placé dans le contexte avec `setUser`. L'utilisateur reste donc synchronisé sans rechargement de page.

### `defaultValue` et `key`

Les champs utilisent `defaultValue`, donc ils sont initialisés à partir du profil.

La clé du formulaire :

```jsx
key={editing ? user?.id : 'register'}
```

permet de recréer le formulaire lorsque l'utilisateur change, ce qui réinitialise correctement les valeurs par défaut.

### Validation HTML

Le navigateur fournit une première validation grâce à :

- `required` ;
- `minLength` ;
- `maxLength` ;
- `type="email"` ;
- `pattern` pour interdire `@` dans le nom d'utilisateur.

Cette validation améliore l'interface, mais le backend doit toujours valider à nouveau les données.

---

## 4.9 `src/Admin/Admin.jsx`

Ce fichier contient trois niveaux de composants :

1. `ResourceForm` ;
2. `ResourcePanel` ;
3. `Admin`.

### `ResourceForm`

Ce composant sert à créer ou modifier une ressource.

#### Props

- `resource` : nom de la ressource, par exemple `users` ;
- `record` : objet à modifier ou objet vide pour une création ;
- `onSaved` : callback après réussite ;
- `onCancel` : callback d'annulation.

#### Détermination du mode

```jsx
const editing = !!record.id
```

Un identifiant indique une modification. L'absence d'identifiant indique une création.

#### Construction dynamique des champs

Les champs viennent de `resources[resource].fields`.

Pour les utilisateurs, le mot de passe devient obligatoire uniquement à la création :

```jsx
resource === 'users' && field[0] === 'password'
  ? [...field.slice(0, 3), !editing, ...field.slice(4)]
  : field
```

#### Conversion du formulaire

Chaque champ est converti avant l'envoi :

- `is_active` devient un booléen ;
- les types `id` et `number` deviennent des nombres ;
- une chaîne vide devient `null` ;
- les autres valeurs restent des chaînes.

Cette conversion est importante car les formulaires HTML renvoient toujours des chaînes.

#### Appel API

Création :

```text
POST /api/{resource}
```

Modification :

```text
PUT /api/{resource}/{id}
```

Après réussite, `onSaved()` ferme le formulaire et recharge la liste.

### `ResourcePanel`

Ce composant affiche une ressource complète :

- titre ;
- bouton de création ;
- formulaire éventuel ;
- erreurs ;
- confirmation de suppression ;
- tableau ;
- pagination.

#### États

- `rows` : lignes de la page courante ;
- `total` : nombre total de lignes ;
- `page` : page courante ;
- `loading` : chargement ;
- `error` : erreur ;
- `notice` : message de réussite ;
- `record` : formulaire ouvert ;
- `deleting` : identifiant dont la suppression est demandée ;
- `busy` : suppression en cours ;
- `revision` : compteur pour relancer le chargement.

#### Liste paginée

```text
GET /api/{resource}?page=1&limit=8
```

Le même composant fonctionne avec les quatre ressources.

#### Colonnes dynamiques

Les colonnes sont déduites des clés présentes dans les lignes reçues :

```jsx
const columns = rows.reduce((names, row) => {
  Object.keys(row).forEach((column) => {
    if (column !== 'full_description' && !names.includes(column)) names.push(column)
  })
  return names
}, [])
```

`full_description` est retirée pour éviter de remplir le tableau avec une longue description.

#### Formatage des valeurs

`formatValue` :

- affiche `—` pour une valeur vide ;
- affiche le nom ou l'email pour un objet lié ;
- affiche `#id` si l'objet n'a pas de nom ni d'email ;
- convertit les autres valeurs en texte.

#### Modification d'une annonce

La liste des annonces fournit un résumé. Avant de modifier une annonce, `edit()` récupère donc son détail complet avec :

```text
GET /api/advertisements/{id}
```

Cela évite d'envoyer un `PUT` incomplet au backend.

#### Suppression

La suppression demande une confirmation puis appelle :

```text
DELETE /api/{resource}/{id}
```

Après succès, le panneau affiche « Enregistrement supprimé. » et recharge les lignes.

### `Admin`

`Admin` choisit la ressource affichée :

```jsx
const [resource, setResource] = useState('advertisements')
```

La barre latérale utilise `Object.entries(resources)` pour créer automatiquement les boutons de navigation.

La clé :

```jsx
<ResourcePanel key={resource} resource={resource} />
```

force un nouveau panneau lorsque l'administrateur change de ressource, ce qui réinitialise ses états locaux.

---

## 4.10 `src/Admin/resources.js`

Ce fichier est une configuration déclarative des ressources administrables.

Chaque entrée contient :

```js
resource: {
  label: '...',
  action: '...',
  fields: [...],
}
```

Chaque champ suit la forme :

```js
[name, label, type, required, maxLength]
```

### `advertisements`

Champs définis :

- titre ;
- description courte ;
- description complète ;
- identifiant de l'entreprise ;
- salaire ;
- lieu ;
- temps de travail ;
- type de contrat ;
- statut actif/inactif.

### `companies`

Champs définis :

- nom ;
- description ;
- email ;
- téléphone ;
- adresse ;
- ville ;
- pays.

### `users`

Champs définis :

- nom d'utilisateur ;
- prénom ;
- nom ;
- email ;
- téléphone ;
- rôle ;
- entreprise liée ;
- mot de passe.

Les rôles possibles sont `user`, `recruiter` et `admin`.

### `applications`

Champs définis :

- identifiant de l'annonce ;
- nom du candidat ;
- email ;
- téléphone ;
- message ;
- statut.

Les statuts possibles sont `pending`, `reviewed`, `accepted` et `rejected`.

L'intérêt de cette configuration est d'éviter quatre implémentations CRUD presque identiques. Pour ajouter un champ simple, il suffit généralement de modifier `resources.js`.

---

# 5. Client HTTP : `src/api.js`

`api.js` est le point commun de tous les appels au backend.

## 5.1 URL de base

```js
const baseUrl = `${(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')}/api`
```

Le frontend prend `VITE_API_URL`, retire son slash final éventuel et ajoute `/api`.

## 5.2 Gestion du token

```js
const tokenKey = 'jobboard-session'
```

`setToken(token)` ajoute ou supprime la valeur de `sessionStorage`.

- token non vide : stockage ;
- token nul ou falsy : suppression.

## 5.3 Fonction `api`

```js
export async function api(path, { body, form, ...options } = {})
```

La fonction accepte :

- le chemin relatif ;
- un corps de requête ;
- le mode formulaire ;
- les options natives de `fetch`.

### Corps JSON

Si `body` est fourni et que `form` est faux, le corps devient :

```js
JSON.stringify(body)
```

avec le header `Content-Type: application/json`.

### Corps de formulaire

Si `form` vaut `true`, le corps devient :

```js
new URLSearchParams(body)
```

Ce mode est utilisé par la connexion.

### Header d'authentification

Si un token est disponible, le header suivant est ajouté :

```http
Authorization: Bearer <token>
```

### Erreur réseau

Une erreur réseau est interceptée par `try/catch`. Les annulations restent reconnaissables avec `AbortError`.

Pour les autres erreurs réseau, le frontend affiche un message indiquant que l'API est inaccessible.

### Réponse vide

Les suppressions réussies utilisent `204 No Content`. Le code retourne alors `null` sans tenter de parser un JSON vide.

### Erreurs HTTP

Le code lit le JSON d'erreur puis traite :

- `401` : suppression du token et événement `session-expired` ;
- erreurs de validation sous forme de tableau ;
- `detail` simple ;
- fallback `Erreur HTTP {status}`.

L'erreur reçoit également la propriété `status`, ce qui permet à un composant de distinguer par exemple un `401` d'un `422`.

---

# 6. Styles

## 6.1 `src/index.css`

Ce fichier contient une initialisation minimale :

```css
body {
  background-color: rgb(246, 234, 219);
  margin: 0;
}
```

`App.css` redéfinit ensuite le fond avec un design plus complet. La présence des deux règles signifie que `App.css`, importé par `App.jsx`, apporte le style final de l'application.

## 6.2 `src/App.css`

`App.css` contient le design transversal.

### Variables CSS

Les variables centralisent les couleurs, les polices et l'ombre principale :

- tons crème et lin ;
- orange/terracotta ;
- brun et espresso ;
- police de titre `Fraunces` ;
- police de texte `DM Sans`.

### Règles générales

Le fichier définit notamment :

- `box-sizing: border-box` ;
- largeur maximale du contenu ;
- styles des liens ;
- hiérarchie des titres ;
- boutons ;
- champs ;
- messages `role="alert"` et `role="status"` ;
- focus visible pour l'accessibilité.

### Page des annonces

Classes importantes :

- `.hero` : en-tête éditorial ;
- `.board-toolbar` : recherche et filtres ;
- `.annonces-list` : grille des offres ;
- `.badge` : badges ;
- `.pagination` : navigation entre les pages.

### Pages d'authentification

Classes importantes :

- `.auth-layout` : mise en page en deux colonnes ;
- `.auth-panel` : partie éditoriale ;
- `.auth-card` : carte du formulaire ;
- `.form-grid` : grille des champs ;
- `.full-width` : champ qui occupe les deux colonnes.

### Administration

Classes importantes :

- `.admin-shell` : sidebar et contenu ;
- `.admin-sidebar` : navigation des ressources ;
- `.resource-panel` : panneau de ressource ;
- `.admin-form` : formulaire CRUD ;
- `.confirmation` : confirmation de suppression ;
- `.table-scroll` : conteneur avec défilement horizontal ;
- `.admin-table` : tableau dynamique.

### Responsive design

Les breakpoints principaux sont :

- `860px` : passage en colonne unique de plusieurs zones ;
- `680px` : adaptation des tableaux et formulaires ;
- `560px` : formulaires et détails sur une seule colonne.

## 6.3 `Header.module.css`

Styles isolés du header :

- `.header` : alignement et largeur maximale ;
- `.brand` : logo et nom du site ;
- `.logoMark` : marque ronde contenant la lettre `t` ;
- `.nav` : liens de navigation ;
- `.link` : lien standard ;
- `.cta` : bouton d'inscription ;
- `.ghostButton` : bouton de déconnexion transparent.

Sur petit écran, la navigation s'aligne à gauche et le header réduit ses marges latérales.

## 6.4 `Advertisement.module.css`

Styles isolés des annonces :

- `.card` construit la carte en grille ;
- `.initial` affiche l'initiale de l'entreprise ;
- `.content` permet au texte de prendre la place disponible ;
- `.job_title` définit le titre ;
- `.meta` affiche les informations secondaires ;
- `.summary` affiche la description courte ;
- `.badges` organise les badges ;
- `.buttons` organise les actions ;
- `.detailGrid` sépare description et métadonnées.

La grille devient verticale sous 720 pixels.

## 6.5 `Login.module.css`

Cette feuille contient une ancienne série de classes génériques :

- `.div` ;
- `.div_box` ;
- `.form` ;
- `.input` ;
- `.div_link` ;
- `.link` ;
- `.login_title`.

Le composant `Login.jsx` actuel ne l'importe pas et utilise principalement les classes globales de `App.css`. Ces styles sont donc présents dans le dépôt mais ne sont pas utilisés par le composant actuel.

## 6.6 `CreateAccount.module.css`

Cette feuille contient les mêmes classes génériques que `Login.module.css` et n'est pas importée par `CreationAccount.jsx` dans la version actuelle.

Les styles réellement utilisés par la page de compte viennent surtout de `App.css`.

---

# 7. Ressource publique

## `public/images/home_icon.png`

Tout fichier placé dans `public/` est servi statiquement par Vite.

Une image située dans :

```text
public/images/home_icon.png
```

peut être référencée dans le navigateur avec :

```text
/images/home_icon.png
```

Le fichier n'est pas importé par les composants React actuels. Il reste néanmoins disponible pour une future utilisation ou une évolution de la navigation.

---

# 8. API utilisée par le frontend

Toutes les routes sont préfixées par `/api`.

| Composant | Méthode | Endpoint | Usage |
| --- | --- | --- | --- |
| `AuthProvider` | `GET` | `/auth/me` | Vérifier la session |
| `AuthProvider` | `POST` | `/auth/login` | Se connecter |
| `Login` | indirect | `/auth/login` | Utilise `login()` |
| `CreationAccount` | `POST` | `/auth/register` | Créer un compte |
| `CreationAccount` | `PUT` | `/auth/me` | Modifier un compte |
| `Annonces` | `GET` | `/advertisements` | Lister les offres |
| `Advertisement` | `GET` | `/advertisements/{id}` | Charger le détail |
| `ApplicationForm` | `POST` | `/advertisements/{id}/applications` | Envoyer une candidature |
| `ResourcePanel` | `GET` | `/{resource}` | Lister une ressource admin |
| `ResourceForm` | `POST` | `/{resource}` | Créer une ressource admin |
| `ResourceForm` | `PUT` | `/{resource}/{id}` | Modifier une ressource admin |
| `ResourcePanel` | `DELETE` | `/{resource}/{id}` | Supprimer une ressource admin |

Le contrat détaillé de ces routes est documenté dans `backend/README.md`.

---

# 9. Cycle d'une interaction complète

Exemple : un administrateur modifie une annonce.

1. `Admin` sélectionne `advertisements`.
2. `ResourcePanel` charge la page avec `GET /api/advertisements`.
3. Le tableau affiche les lignes reçues.
4. L'administrateur clique sur « Modifier ».
5. Le frontend charge le détail complet de l'annonce.
6. `ResourceForm` construit les champs depuis `resources.js`.
7. L'administrateur valide le formulaire.
8. Les chaînes HTML sont converties en nombres, booléens ou `null`.
9. `api.js` sérialise l'objet en JSON.
10. `PUT /api/advertisements/{id}` est envoyé avec le JWT.
11. Le backend vérifie l'identité et le rôle admin.
12. Après succès, `reload()` recharge le tableau.
13. L'interface affiche une notification de réussite.

---

# 10. Lancer et vérifier le frontend

Depuis le dossier `frontend/` :

```bash
npm install
cp .env.example .env
npm run dev
```

Tests de qualité disponibles :

```bash
npm run lint
npm run build
```

Le backend doit être lancé séparément. Par défaut, le frontend s'attend à trouver l'API sur :

```text
http://127.0.0.1:8000/api
```

L'origine du frontend doit être autorisée par `CORS_ORIGINS` dans la configuration backend.

---

# 11. Points importants à retenir

1. `App.jsx` orchestre la navigation, mais les composants de page portent la logique métier d'interface.
2. `AuthProvider.jsx` est la source frontend de vérité pour l'utilisateur connecté.
3. `api.js` est le seul point commun de communication HTTP.
4. Le token JWT est conservé dans `sessionStorage` et envoyé dans `Authorization`.
5. Les annonces sont chargées avec pagination et recherche côté API.
6. Les détails d'une annonce sont chargés à la demande.
7. Une candidature peut être anonyme ou associée au compte connecté.
8. L'administration est générée à partir de `resources.js` afin d'éviter de dupliquer le CRUD.
9. Les protections frontend ne remplacent pas les vérifications backend.
10. `App.css` contient la majorité des styles actuellement utilisés ; les modules CSS de login et de compte sont présents mais ne sont pas importés dans leurs composants.
