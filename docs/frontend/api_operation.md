# Fonctionnement de l'API

## 1. Vue d'ensemble

L'API est un backend FastAPI situé dans :

```text
backend/app/
```

Son rôle est de recevoir les requêtes du frontend, de vérifier les données, d'interroger la base MySQL et de renvoyer une réponse JSON.

Le point d'entrée est :

```text
backend/app/main.py
```

Il active :

- FastAPI ;
- le CORS pour autoriser le frontend ;
- toutes les routes `/api`.

Les routes sont regroupées dans :

```text
backend/app/api/router.py
```

Le préfixe général est :

```python
api_router = APIRouter(prefix="/api")
```

Donc une route définie comme :

```python
@router.post("/login")
```

avec un router ayant le préfixe `/auth` devient :

```text
POST /api/auth/login
```

---

## 2. Fonctionnement général d'une requête

Une requête suit globalement ce chemin :

```text
Frontend
   ↓
api.js
   ↓
Requête HTTP vers /api/...
   ↓
Route FastAPI
   ↓
Validation des données avec Pydantic
   ↓
Vérification de l'utilisateur et des permissions
   ↓
Requête SQLAlchemy vers MySQL
   ↓
Commit éventuel
   ↓
Réponse JSON
```

Exemple :

```text
POST /api/auth/login
```

devient :

```text
Login.jsx
   ↓
AuthProvider.login()
   ↓
api('/auth/login')
   ↓
auth.py
   ↓
verification du mot de passe
   ↓
création du JWT
   ↓
réponse JSON
```

---

## 3. Les différents types de requêtes HTTP

### `GET`

Récupérer des données.

Exemples :

```text
GET /api/advertisements
GET /api/advertisements/4
GET /api/companies
GET /api/auth/me
```

### `POST`

Créer une donnée ou déclencher une action.

Exemples :

```text
POST /api/auth/login
POST /api/auth/register
POST /api/advertisements
POST /api/advertisements/4/applications
```

### `PUT`

Modifier une donnée existante.

Exemples :

```text
PUT /api/auth/me
PUT /api/users/3
PUT /api/companies/2
```

### `DELETE`

Supprimer une donnée.

Exemples :

```text
DELETE /api/users/3
DELETE /api/advertisements/4
```

---

## 4. Les routes d'authentification

Fichier :

```text
backend/app/api/routes/auth.py
```

### `POST /api/auth/register`

Crée un compte utilisateur.

Le backend :

1. valide les données avec `RegisterIn` ;
2. hash le mot de passe avec bcrypt ;
3. crée l'utilisateur avec le rôle `user` ;
4. l'enregistre en base ;
5. renvoie l'utilisateur créé.

Le mot de passe en clair n'est jamais enregistré.

### `POST /api/auth/login`

Authentifie un utilisateur.

Le backend :

1. recherche l'utilisateur par nom ou email ;
2. vérifie le mot de passe avec bcrypt ;
3. crée un JWT ;
4. renvoie le token, le rôle et l'identifiant utilisateur.

Réponse approximative :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "user",
  "user_id": 4
}
```

Le frontend place ensuite le token dans :

```text
sessionStorage["jobboard-session"]
```

### `GET /api/auth/me`

Renvoie l'utilisateur connecté.

Le frontend envoie :

```text
Authorization: Bearer eyJ...
```

Le backend vérifie le token, récupère l'identifiant utilisateur et renvoie ses informations.

### `PUT /api/auth/me`

Modifie le profil de l'utilisateur connecté.

Cette route peut modifier :

- le nom d'utilisateur ;
- le prénom ;
- le nom ;
- l'email ;
- le téléphone ;
- le mot de passe.

Pour changer le mot de passe, l'ancien mot de passe doit être fourni et vérifié.

---

## 5. Les routes des offres d'emploi

Fichier :

```text
backend/app/api/routes/advertisements.py
```

Préfixe :

```text
/api/advertisements
```

### `GET /api/advertisements`

Liste les offres.

Les utilisateurs non administrateurs ne voient que les offres actives.

Filtres possibles :

```text
GET /api/advertisements?q=python
GET /api/advertisements?location=Paris
GET /api/advertisements?contract_type=CDI
GET /api/advertisements?company_id=2
```

Pagination :

```text
?page=1&limit=20
```

Réponse :

```json
{
  "items": [],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

### `GET /api/advertisements/{id}`

Récupère une offre précise.

Une offre inactive est invisible pour un utilisateur normal, mais reste accessible à un administrateur.

### `POST /api/advertisements`

Crée une offre. Cette route nécessite un utilisateur administrateur.

Le backend valide le JSON, vérifie le rôle, crée l'offre et la renvoie.

### `PUT /api/advertisements/{id}`

Modifie une offre existante. Cette route est réservée aux administrateurs.

### `DELETE /api/advertisements/{id}`

Supprime une offre. Cette route est réservée aux administrateurs.

### `POST /api/advertisements/{id}/applications`

Permet de postuler à une offre.

Cette route peut être utilisée par un utilisateur connecté ou anonyme.

Pour un utilisateur connecté, les informations du profil sont utilisées automatiquement.

Pour un utilisateur anonyme, les données suivantes sont nécessaires :

```json
{
  "applicant_name": "Jean Dupont",
  "applicant_email": "jean@example.com",
  "applicant_phone": "0600000000",
  "message": "Ma candidature..."
}
```

Un utilisateur ne peut pas postuler deux fois à la même offre. La route possède également une limitation de fréquence.

---

## 6. Les routes des entreprises

Fichier :

```text
backend/app/api/routes/companies.py
```

Préfixe :

```text
/api/companies
```

Routes publiques :

```text
GET /api/companies
GET /api/companies/{id}
```

Filtre possible :

```text
GET /api/companies?q=paris
```

Routes administrateur :

```text
POST /api/companies
PUT /api/companies/{id}
DELETE /api/companies/{id}
```

Ces routes nécessitent un JWT valide avec le rôle `admin`.

---

## 7. Les routes des utilisateurs

Fichier :

```text
backend/app/api/routes/users.py
```

Préfixe :

```text
/api/users
```

Toutes les routes de ce fichier sont réservées aux administrateurs.

### `GET /api/users`

Liste les utilisateurs.

Filtres possibles :

```text
GET /api/users?q=jean
GET /api/users?role=admin
GET /api/users?company_id=2
```

### `GET /api/users/{id}`

Récupère un utilisateur précis.

### `POST /api/users`

Crée un utilisateur depuis l'administration. Le mot de passe est hashé avant l'enregistrement.

### `PUT /api/users/{id}`

Modifie un utilisateur. Un administrateur ne peut pas supprimer son propre rôle administrateur.

### `DELETE /api/users/{id}`

Supprime un utilisateur. Un administrateur ne peut pas supprimer son propre compte.

---

## 8. Les routes des candidatures

Fichier :

```text
backend/app/api/routes/applications.py
```

Préfixe :

```text
/api/applications
```

Ces routes sont réservées aux administrateurs.

### `GET /api/applications`

Liste les candidatures.

Filtres possibles :

```text
GET /api/applications?advertisement_id=4
GET /api/applications?user_id=2
GET /api/applications?status=pending
GET /api/applications?q=jean
```

### `GET /api/applications/{id}`

Récupère une candidature précise.

### `POST /api/applications`

Crée directement une candidature depuis l'administration.

### `PUT /api/applications/{id}`

Modifie une candidature, notamment son statut.

### `DELETE /api/applications/{id}`

Supprime une candidature.

---

## 9. Fonctionnement des permissions

Le fichier central est :

```text
backend/app/api/deps.py
```

### Requête publique

Aucun token obligatoire.

Exemples :

```text
GET /api/advertisements
GET /api/companies
POST /api/auth/register
```

### Requête nécessitant une connexion

Le backend exige :

```text
Authorization: Bearer <jwt>
```

Si le token est absent ou invalide, la réponse est :

```text
401 Unauthorized
```

Exemples :

```text
GET /api/auth/me
PUT /api/auth/me
```

### Requête administrateur

Le backend vérifie que :

```python
user.role == "admin"
```

Si l'utilisateur est connecté mais n'est pas administrateur :

```text
403 Forbidden
```

---

## 10. Validation des données

Les données entrantes sont validées par les schémas Pydantic dans :

```text
backend/app/schemas/
```

Exemples :

```text
RegisterIn
ProfileUpdate
AdvertisementIn
CompanyIn
UserCreate
ApplicationIn
```

Si les données ne respectent pas le format attendu, l'API renvoie généralement :

```text
422 Unprocessable Entity
```

Exemples : email invalide ou champ obligatoire manquant.

---

## 11. Gestion des erreurs

Le fichier :

```text
backend/app/api/errors.py
```

centralise notamment les erreurs de base de données.

| Situation | Réponse |
|---|---:|
| Données invalides | `422` |
| Token absent ou invalide | `401` |
| Utilisateur connecté mais non-admin | `403` |
| Ressource inexistante | `404` |
| Doublon en base | `409` |
| Trop de requêtes | `429` |
| Succès sans contenu | `204` |

La fonction `get_or_404()` renvoie `404` si une ressource n'existe pas.

La fonction `commit()` transforme certaines erreurs MySQL en réponses HTTP compréhensibles.

---

## 12. Pagination

Les routes de liste utilisent :

```text
backend/app/api/pagination.py
```

Paramètres disponibles :

```text
page
limit
```

Exemple :

```text
GET /api/users?page=2&limit=10
```

La réponse contient :

```json
{
  "items": [],
  "total": 35,
  "page": 2,
  "limit": 10
}
```

Le backend compte le nombre total de résultats, calcule le décalage, récupère la page demandée et renvoie les éléments avec les informations de pagination.

---

## 13. Résumé du fonctionnement

```text
1. Le frontend prépare une requête avec api.js.
2. api.js ajoute le JWT s'il existe.
3. FastAPI reçoit la requête.
4. Pydantic vérifie les données.
5. Les dépendances vérifient l'utilisateur et son rôle.
6. La route exécute une requête SQLAlchemy.
7. La base MySQL est lue ou modifiée.
8. Le backend renvoie du JSON et un code HTTP.
9. Le frontend traite la réponse ou affiche l'erreur.
```

Les principaux groupes de l'API sont :

```text
/auth              Connexion, inscription, profil
/advertisements    Offres d'emploi et candidatures publiques
/companies         Entreprises
/users             Gestion des utilisateurs par les admins
/applications      Gestion des candidatures par les admins
```

Exemples de parcours :

```text
Se connecter :
POST /api/auth/login
GET  /api/auth/me

Afficher les offres :
GET /api/advertisements

Créer une offre :
POST /api/advertisements
Authorization: Bearer <jwt-admin>

Postuler :
POST /api/advertisements/4/applications

Gérer les utilisateurs :
GET/POST/PUT/DELETE /api/users
Authorization: Bearer <jwt-admin>
```
