# Fonctionnement de l'authentification

## 1. Frontend React

### `frontend/src/Login/Login.jsx`

Page de connexion.

Responsabilités :

- affiche les champs `username` et `password` ;
- récupère les valeurs du formulaire ;
- appelle la fonction `login(body)` ;
- affiche les erreurs ;
- redirige l'utilisateur selon son rôle :

```jsx
navigate(user.role === 'admin' ? '/Admin' : '/Annonces')
```

Ce fichier ne vérifie pas directement le mot de passe. Il délègue cette tâche à `AuthProvider`.

---

### `frontend/src/AuthProvider.jsx`

Gestionnaire central de la session côté frontend.

Il contient notamment :

```jsx
async function login(credentials) { ... }
function logout() { ... }
```

La fonction `login()` :

1. appelle `POST /api/auth/login` ;
2. récupère le JWT reçu ;
3. stocke le JWT avec `setToken()` ;
4. appelle ensuite `GET /api/auth/me` ;
5. stocke l'utilisateur dans `user`.

Les données sont rendues accessibles à toute l'application grâce à :

```jsx
<AuthContext.Provider value={{ user, loading, login, logout, setUser }}>
```

Le provider vérifie également automatiquement la session au démarrage de l'application.

---

### `frontend/src/auth.js`

Définit le contexte React :

```jsx
export const AuthContext = createContext(null)
```

Il fournit aussi le hook :

```jsx
export function useAuth() {
  return useContext(AuthContext)
}
```

Grâce à lui, les composants peuvent récupérer :

```jsx
const { user, login, logout } = useAuth()
```

Ce fichier ne réalise pas lui-même l'authentification. Il sert de passerelle vers `AuthProvider`.

---

### `frontend/src/api.js`

Client HTTP central de l'application.

Il :

- envoie les requêtes vers le backend ;
- récupère le token depuis `sessionStorage` ;
- ajoute le token aux requêtes dans l'en-tête `Authorization: Bearer <token>` ;
- stocke ou supprime le token avec `setToken()` ;
- détecte les réponses `401 Unauthorized` ;
- supprime la session et déclenche `session-expired` en cas de token invalide ou expiré.

---

### `frontend/src/App.jsx`

Protège les routes privées avec le composant :

```jsx
function Protected({ children, admin = false }) { ... }
```

Il vérifie notamment :

```jsx
if (!user) return <Navigate to="/Login" replace />
```

Pour la page administrateur :

```jsx
if (admin && user.role !== 'admin') {
  return <Navigate to="/Annonces" replace />
}
```

Les routes protégées sont :

```jsx
<Route path="/Account" element={<Protected>...</Protected>} />
<Route path="/Admin" element={<Protected admin><Admin /></Protected>} />
```

`App.jsx` place aussi toute l'application à l'intérieur de `AuthProvider` :

```jsx
<AuthProvider>
  ...
</AuthProvider>
```

---

### `frontend/src/Header/Header.jsx`

Utilise l'utilisateur connecté et permet la déconnexion :

```jsx
const { user, logout } = useAuth()
```

Lors d'une déconnexion :

```jsx
logout()
navigate('/Annonces')
```

La fonction `logout()` supprime le token et remet `user` à `null`.

---

### `frontend/src/Create_Account/CreationAccount.jsx`

Gère :

- l'inscription ;
- la modification du profil ;
- le changement de mot de passe.

Lors de l'inscription :

```jsx
await api('/auth/register', { method: 'POST', body })
await login({ username: body.user_name, password: body.password })
```

Après la création du compte, l'utilisateur est donc automatiquement connecté.

Pour modifier le profil :

```jsx
api('/auth/me', { method: 'PUT', body })
```

---

### `frontend/src/main.jsx`

Démarre l'application React et active le routage avec `BrowserRouter`.

Il ne gère pas directement les identifiants, mais permet à `App.jsx` d'utiliser les routes comme `/Login`, `/Admin` et `/Account`.

---

## 2. Backend FastAPI

### `backend/app/api/routes/auth.py`

Fichier principal de l'authentification côté backend.

Il contient les routes :

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
PUT  /api/auth/me
```

#### `POST /api/auth/login`

Cette route :

1. reçoit le nom d'utilisateur/email et le mot de passe ;
2. recherche l'utilisateur en base ;
3. vérifie le mot de passe ;
4. crée un JWT ;
5. renvoie le token, le rôle et l'identifiant utilisateur.

```python
return TokenOut(
    access_token=create_access_token(user.id, user.role),
    role=user.role,
    user_id=user.id,
)
```

#### `GET /api/auth/me`

Renvoie l'utilisateur actuellement authentifié :

```python
def read_me(user: CurrentUser):
    return user
```

#### `POST /api/auth/register`

Crée un nouvel utilisateur et hash son mot de passe avant de le stocker.

---

### `backend/app/api/deps.py`

Vérifie les tokens reçus sur les routes protégées.

Il utilise :

```python
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False
)
```

Fonctionnement :

1. récupère le token dans `Authorization: Bearer ...` ;
2. décode le JWT ;
3. récupère l'identifiant utilisateur dans `sub` ;
4. recherche l'utilisateur en base ;
5. renvoie l'utilisateur authentifié.

Dépendances principales :

- `OptionalUser` : l'utilisateur peut être anonyme ;
- `CurrentUser` : l'utilisateur doit être connecté ;
- `AdminUser` : l'utilisateur doit être connecté et avoir le rôle `admin`.

---

### `backend/app/core/security.py`

Contient les fonctions cryptographiques.

#### Hashage du mot de passe

```python
hash_password(password)
```

Utilise bcrypt pour ne jamais stocker le mot de passe en clair.

#### Vérification du mot de passe

```python
verify_password(password, hashed_password)
```

Compare le mot de passe fourni avec le hash stocké.

#### Création du JWT

```python
create_access_token(user_id, role)
```

Le token contient :

```python
{
    "sub": "identifiant utilisateur",
    "role": "user ou admin",
    "exp": "date d'expiration"
}
```

#### Décodage du JWT

```python
decode_access_token(token)
```

Vérifie que le token est correctement signé, non expiré et utilise le bon algorithme.

---

### `backend/app/core/config.py`

Contient la configuration de sécurité :

```python
secret_key
access_token_expire_minutes
algorithm
```

Valeurs par défaut importantes :

```python
access_token_expire_minutes = 60
algorithm = "HS256"
```

La `secret_key` sert à signer et vérifier les JWT. Elle est chargée depuis `.env`.

---

### `backend/app/schemas/auth.py`

Définit le format des données d'authentification.

- `RegisterIn` : champs nécessaires à la création d'un compte ;
- `ProfileUpdate` : champs autorisés pour modifier le compte et le mot de passe ;
- `TokenOut` : format de la réponse de connexion.

Réponse de connexion :

```python
{
    "access_token": "...",
    "token_type": "bearer",
    "role": "...",
    "user_id": 1
}
```

---

### `backend/app/api/router.py`

Enregistre les routes d'authentification dans l'API :

```python
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
```

Les routes de `auth.py` deviennent donc accessibles sous `/api/auth/...`.

---

## 3. Fichiers de sécurité complémentaires

### `backend/app/api/rate_limit.py`

Limite le nombre de tentatives de connexion.

La route `/api/auth/login` utilise :

```python
dependencies=[Depends(login_rate_limit)]
```

Cela évite qu'un utilisateur ou un bot essaie rapidement un grand nombre de mots de passe.

---

### `backend/app/schemas/common.py`

Définit notamment les contraintes sur les mots de passe :

- longueur maximale compatible avec bcrypt ;
- validation des noms d'utilisateur ;
- autres types réutilisés par les schémas d'authentification.

---

### `backend/app/models.py`

Contient le modèle SQLAlchemy `User` utilisé pour stocker les utilisateurs en base.

Il contient notamment :

- l'identifiant ;
- le nom d'utilisateur ;
- l'email ;
- le hash du mot de passe ;
- le rôle ;
- les informations du profil.

---

## 4. Parcours complet

```text
Login.jsx
    ↓
useAuth()
    ↓
AuthProvider.login()
    ↓
api('/auth/login')
    ↓
auth.py : route POST /api/auth/login
    ↓
security.py : verify_password()
    ↓
security.py : create_access_token()
    ↓
JWT retourné au frontend
    ↓
api.js : stockage dans sessionStorage
    ↓
api('/auth/me')
    ↓
deps.py : décodage et validation du JWT
    ↓
Utilisateur connecté stocké dans AuthProvider
```

## Fichiers essentiels à retenir

```text
frontend/src/Login/Login.jsx
frontend/src/AuthProvider.jsx
frontend/src/auth.js
frontend/src/api.js
frontend/src/App.jsx
backend/app/api/routes/auth.py
backend/app/api/deps.py
backend/app/core/security.py
backend/app/core/config.py
backend/app/schemas/auth.py
```
