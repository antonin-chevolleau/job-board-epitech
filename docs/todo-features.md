# Job Board — Todo des features

> Stack retenue : FastAPI + SQLAlchemy + PyMySQL + MySQL (back) · React + React Router DOM + CSS Modules (front)

## 1. Base de données (MySQL)

- [x] Créer la base MySQL et la connexion (SQLAlchemy + PyMySQL, variables dans `.env`)
  - [x] DB créée et hébergée sur aiven
  - [x] Initialiser FastAPI
  - [x] Initialiser SQLAlchemy
  - [x] Initialiser PyMySQL
  - [x] Initialiser le `.env`
- [x] Table `companies` (entreprises)
- [x] Table `advertisements` (annonces : titre, description courte, description complète, salaire, lieu, temps de travail, entreprise)
- [x] Table `people` (candidats ; champ de rôle pour distinguer l'admin)
- [x] Table `applications` (candidatures : personne, annonce, message, date)
- [x] Relations et clés étrangères entre les tables
- [x] Champs cohérents avec les informations affichées sur le front
- [/] Remplir la base via le backend (pas d'insertion manuelle)
- [/] Prévoir un compte admin (seed ou champ de rôle)
  - [x] Champ de rôle (`people.role`)
  - [ ] Seed du compte admin

## 2. API (FastAPI)

- [x] Structure du projet + schémas Pydantic (validation / sérialisation)
- [ ] CRUD `companies`
- [x] CRUD `advertisements`
  - [x] `GET /advertisements` (liste)
  - [x] `GET /advertisements/{id}`
  - [x] `POST`
  - [x] `PATCH`
  - [x] `DELETE`
- [ ] CRUD `people`
- [ ] CRUD `applications`
- [ ] Verbes HTTP corrects et routes RESTful
- [ ] Endpoint de candidature (enregistrement en BDD)
- [ ] Authentification (inscription, connexion, modification de compte)
- [ ] Protection des routes d'administration (admin uniquement, côté API)
- [ ] Pagination sur les listes
- [ ] Toutes les données dynamiques du front passent par l'API
- [x] Configuration CORS pour le front
- [x] Linter / formatage avec Ruff
- [ ] Tests (pytest)

## 3. Front — Job board (page principale)

- [ ] Liste des annonces (titre, courte description)
- [ ] Bouton « Learn more » : détails complets via l'API, sans rechargement, sans popup
- [ ] Bouton « Apply » : ouverture du formulaire de candidature
- [ ] Formulaire : nom, email, téléphone, message au propriétaire de l'annonce
- [ ] Candidature enregistrée en BDD
- [ ] Gestion des états (chargement, erreurs, confirmation d'envoi)

## 4. Front — Authentification

- [ ] Page de connexion
- [ ] Page de création / modification de compte
- [ ] Utilisateur connecté : infos pré-remplies dans le formulaire de candidature
- [ ] Redirection après connexion : admin → administration, autre → job board
- [ ] Routes protégées (React Router DOM)

## 5. Front — Administration

- [ ] Accès réservé à l'admin
- [ ] Lister les enregistrements de toutes les tables
- [ ] Créer un enregistrement
- [ ] Modifier un enregistrement
- [ ] Supprimer un enregistrement
- [ ] Pagination des listes
- [ ] Mise en page simple et conviviale

## 6. Design et qualité

- [ ] Fonctionnalités d'abord, puis raffinement du design
- [ ] Design soigné (CSS Modules, UX globale agréable)
- [ ] Lint front avec ESLint
- [ ] Tout tester en local

## 7. Livraison

- [ ] README : installation, configuration, lancement
- [ ] README : schéma de la base de données
- [ ] README : routes de l'API
- [ ] README : pages du front

## 8. Déploiement (selon les specs techniques)

- [ ] Back-end sur Render
- [ ] Front-end sur Vercel
- [ ] BDD sur Aiven

## Points à clarifier

- [ ] Envoi réel d'emails ou simple enregistrement en base ?
- [ ] Périmètre de la « collecte » d'offres (scraping / import) ?
- [ ] Mécanisme d'authentification (sessions ou JWT)
