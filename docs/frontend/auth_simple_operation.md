# Pourquoi plusieurs fichiers pour le login ?

Oui, on peut simplifier. Mais les fichiers actuels ont des rôles différents :

```text
Login.jsx
   ↓
AuthProvider
   ↓
api.js
   ↓
Backend
```

## Rôle de chaque fichier

### `Login.jsx`

Gère uniquement l'interface :

- affiche le formulaire ;
- récupère `username` et `password` ;
- affiche les erreurs ;
- redirige après connexion.

Il ne devrait pas gérer directement le token ou les requêtes HTTP.

### `AuthProvider.jsx`

Gère l'état global de la session :

- sait quel utilisateur est connecté ;
- contient `login()` et `logout()` ;
- restaure la session au rechargement ;
- informe toute l'application lorsqu'un utilisateur se connecte ou se déconnecte.

Sans lui, chaque composant devrait gérer son propre état de connexion.

### `auth.js`

Il est très léger :

```jsx
export function useAuth() {
  return useContext(AuthContext)
}
```

Il ne fait pas réellement une étape réseau. Il fournit simplement un raccourci pour accéder à `AuthProvider` :

```jsx
const { login } = useAuth()
```

### `api.js`

Centralise les requêtes HTTP :

- ajoute automatiquement le token ;
- gère les erreurs HTTP ;
- supprime la session lorsqu'un token expire ;
- évite de répéter `fetch()` dans tous les composants.

Sans `api.js`, il faudrait écrire partout :

```jsx
fetch(url, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
```

## Le login ne passe donc pas vraiment par quatre systèmes

Le parcours réel est plutôt :

```text
Login.jsx
  → appelle login()

AuthProvider
  → appelle api('/auth/login')

api.js
  → fait le fetch HTTP et ajoute le token

Backend
  → vérifie les identifiants et renvoie le JWT
```

`auth.js` ne fait qu'exposer le contexte. Il n'envoie aucune requête.

## Peut-on simplifier ?

Oui, par exemple en supprimant `auth.js` et en utilisant directement `AuthContext` :

```jsx
import { useContext } from 'react'
import { AuthContext } from '../auth'

const { login } = useContext(AuthContext)
```

Mais ce serait moins propre, car tous les composants devraient connaître le fonctionnement interne du contexte.

On pourrait aussi mettre le `fetch('/auth/login')` directement dans `Login.jsx`, mais cela mélangerait :

- l'affichage ;
- la gestion de session ;
- le stockage du token ;
- la communication avec l'API.

## Organisation actuelle recommandée

L'organisation actuelle suit une séparation classique :

```text
Login.jsx       = interface
 auth.js        = accès au contexte
AuthProvider    = état global de session
api.js          = communication HTTP
Backend         = vérification réelle
```

Le nombre de fichiers paraît important, mais chaque fichier a une responsabilité précise. Pour un petit projet, une version plus simple pourrait regrouper `auth.js` et `AuthProvider.jsx`, mais il est préférable de conserver `api.js`, car il est utilisé par toutes les requêtes de l'application.
