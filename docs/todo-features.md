# Job Board — État du projet

Sujet : `sujets/jobBoard-project.pdf`. Installation : `README.md` et `docs/setup-local.md`.
Contrat d'API : `backend/README.md`.

## 1. Base de données

- [x] Schéma SQL : `companies`, `users`, `advertisements`, `job_applications`
- [x] Relations, clés étrangères, suppressions en cascade / SET NULL
- [x] Données de démonstration (`backend/sql/seed.sql`)
- [x] Requêtes SQL d'entraînement (`docs/bootstrap-queries.sql`)

## 2. API

- [x] CRUD annonces, entreprises, utilisateurs et candidatures (admin)
- [x] Liste publique des annonces actives avec filtres (`q`, `location`, `contract_type`, `company_id`)
- [x] Candidature visiteur ou connecté, doublons refusés
- [x] Inscription, connexion (JWT), lecture et modification du compte
- [x] Mots de passe bcrypt, contrôle des rôles côté serveur
- [x] Pagination `{items, total, page, limit}`, erreurs 401/403/404/409/422
- [x] Limitation de débit (login, candidature)
- [x] Notification email optionnelle (SMTP)
- [x] Tests pytest

## 3. Frontend

- [x] Liste paginée des annonces, recherche et filtres faits par l'API
- [x] Détails chargés à la demande, sans rechargement ni popup
- [x] Formulaire de candidature (coordonnées du compte pour un utilisateur connecté)
- [x] Inscription, connexion, modification du profil
- [x] Retour à la connexion quand la session a expiré au moment de postuler
- [x] Administration protégée : listes paginées, création, modification, suppression
- [x] Interface en français

## 4. À faire plus tard

- [ ] Droits du rôle `recruiter` (publier ses annonces, voir leurs candidatures)
- [ ] « Mes candidatures » pour l'utilisateur connecté (route + page)
- [ ] Changement de mot de passe depuis `/Account` (déjà géré par `PUT /api/auth/me`)
- [ ] « Se souvenir de moi » à la connexion
- [ ] Admin : listes déroulantes pour `company_id` / `user_id`, mise en forme des colonnes
- [ ] Vérification d'email et récupération du mot de passe
- [ ] Test de l'envoi SMTP réel
