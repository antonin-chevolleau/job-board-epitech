# Job Board — Résumé du sujet (Epitech, v4.0.0)

> Slogan du sujet : _« Code your way to your next job »_

## 1. Contexte et objectif

Les offres d'emploi et de stage sont dispersées sur de nombreuses plateformes, avec des annonces similaires ou en doublon, ce qui rend la recherche chronophage.

**Objectif du projet** : construire une solution qui **collecte des offres** et aide les utilisateurs à **trouver des opportunités pertinentes**. Le projet est directement lié à ta propre recherche d'emploi / d'alternance.

---

## 2. Livrables attendus (vue d'ensemble)

| Composant           | Description                                                                        |
| ------------------- | ---------------------------------------------------------------------------------- |
| **Base de données** | Stockage des annonces (SQL)                                                        |
| **Front end**       | Page web en technologies **JavaScript** : job board public + page d'administration |
| **Back end (API)**  | Permet aux utilisateurs de postuler ; gère la BDD en **CRUD** (réservé à l'admin)  |
| **README**          | Documentation d'installation, configuration, exécution et composants               |

> ⚠️ **Contrainte générale : tout le travail doit être testé en local.**

---

## 3. Base de données

**Type** : base de données **SQL**.

### Tables minimales obligatoires

1. **Annonces** (advertisements)
2. **Entreprises** (companies)
3. **Personnes** : celles qui sont en charge d'une annonce **ou** qui y postulent
4. **Candidatures** (job applications) : informations sur la candidature (emails envoyés, personne et annonce concernées, etc.)

### Règles

- Les champs de la BDD doivent être **cohérents avec les informations affichées sur les pages web**.
- Tu peux ajouter **autant de tables/champs pertinents** que tu veux.
- La BDD doit être **remplie via ton backend** (pas d'insertion manuelle comme méthode principale).

---

## 4. API (back end)

- Expose des opérations **CRUD** (Create, Read, Update, Delete) sur **les tables** de la base.
- **Toutes les données dynamiques affichées par le front doivent passer par cette API.**
- ⚠️ Respecter les **verbes HTTP appropriés** et les **règles de routage RESTful**.
- **Langage libre**. Exemples cités : Python (Flask ou FastAPI), Node.js (Express.js), PHP (Laravel ou Lumen), etc.

---

## 5. Front end

### 5.1 Job board (page principale)

Page **HTML/CSS** listant les annonces. Chaque annonce affiche **au minimum** :

- un **titre** ;
- une **courte description** ;
- un bouton **« Learn more »** ;
- un bouton **« Apply »**.

#### Bouton « Learn more »

- Affiche **toutes les informations disponibles** sur l'annonce (description complète, salaire, lieu, temps de travail, etc.).
- Données **récupérées dynamiquement via l'API**, **sans rechargement de la page**.
- **Pas de popup.**

#### Bouton « Apply »

Ouvre un formulaire permettant à l'utilisateur de :

- saisir ses informations (nom, email, téléphone, etc.) ;
- **envoyer un message au propriétaire de l'annonce** (c'est-à-dire toi).

➡️ **Chaque candidature doit être enregistrée en base de données.**

### 5.2 Authentification

- Les utilisateurs peuvent **se connecter**.
- Une fois identifié, l'utilisateur **n'a plus besoin de ressaisir ses informations personnelles** pour postuler.
- Pages requises :
  - une page de **connexion** ;
  - une page de **création / modification de compte**.
- Redirection après connexion réussie :
  - **admin** → page d'administration ;
  - **autre utilisateur** → job board.

### 5.3 Administration

Page **HTML/CSS** permettant à l'admin de surveiller la base de données. Depuis cette page, l'admin peut :

- **lister** tous les enregistrements de toutes les tables ;
- **créer** de nouveaux enregistrements ;
- **modifier** ou **supprimer** les enregistrements existants.

Contraintes :

- Accessible **uniquement par un admin**.
- Prévoir une **pagination** pour les longues listes.
- Mise en page libre, mais **simple et conviviale**.

### 5.4 Design

- Design libre, mais il doit être **soigné** : feuilles de style propres et expérience utilisateur globale agréable.
- Conseil du sujet : **d'abord les fonctionnalités, puis raffiner le design** une fois que tout fonctionne.

---

## 6. Livraison

Le rendu doit inclure un **README** expliquant :

- comment **installer**, **configurer** et **lancer** le projet ;
- ses **composants principaux** :
  - le **schéma de la base de données** ;
  - les **routes de l'API** ;
  - les **pages**.

---

## 7. Checklist de cadrage

### Base de données

- [ ] Base SQL
- [ ] Table annonces
- [ ] Table entreprises
- [ ] Table personnes (responsables / candidats)
- [ ] Table candidatures (emails envoyés, personne, annonce, etc.)
- [ ] Champs cohérents avec ce qui est affiché sur le front
- [ ] Remplissage de la BDD via le backend

### API

- [ ] CRUD sur toutes les tables
- [ ] Verbes HTTP corrects et routes RESTful
- [ ] Toutes les données dynamiques du front passent par l'API
- [ ] Opérations d'administration réservées à l'admin
- [ ] Endpoint de candidature

### Job board

- [ ] Liste des annonces (titre, courte description, « Learn more », « Apply »)
- [ ] « Learn more » : détails via l'API, sans rechargement, sans popup
- [ ] « Apply » : formulaire (infos personnelles + message au propriétaire)
- [ ] Candidature enregistrée en BDD

### Authentification

- [ ] Page de connexion
- [ ] Page de création / modification de compte
- [ ] Utilisateur connecté : infos pré-remplies pour postuler
- [ ] Redirection : admin → administration, autre → job board

### Administration

- [ ] Liste / création / modification / suppression sur toutes les tables
- [ ] Accès réservé à l'admin
- [ ] Pagination

### Qualité et rendu

- [ ] Design soigné (CSS, UX)
- [ ] Tout testé en local
- [ ] README (installation, configuration, lancement, schéma BDD, routes API, pages)

---

## 8. Points d'attention (notes personnelles, non issues du sujet)

Le sujet laisse certains points ouverts. Ce sont des **choix à faire de ton côté** :

- **Stack** : langage/framework du backend, SGBD précis (SQLite, MySQL, PostgreSQL…), framework JS ou JS « vanilla » pour le front (le sujet dit seulement « technologies JavaScript »).
- **Mécanisme d'authentification** : non imposé (sessions, JWT…). À prévoir pour protéger à la fois l'accès à la page admin **et** les routes d'API correspondantes (la protection côté front seule ne suffit pas).
- **Envoi d'emails** : la table candidatures mentionne des « emails envoyés ». Le sujet ne dit pas si un vrai envoi est attendu ; à clarifier ou à gérer au minimum par un enregistrement en base.
- **Notion de « collecte » d'offres** : l'intro parle de collecter des offres, mais les exigences détaillées portent sur le stockage et la gestion via l'API et l'admin. Le périmètre exact du scraping/import n'est pas précisé.
- **Rôle admin** : prévoir comment un utilisateur devient admin (champ de rôle en BDD, compte seedé, etc.).
