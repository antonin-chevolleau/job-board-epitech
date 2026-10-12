# Job Board — État de la livraison

Référence finale : `sujets/jobBoard-project.pdf`. Guide d'intégration :
`sujets/jobBoard-bootstrap.pdf`. Installation et limites : `README.md`.

## 1. Base de données

- [x] Modèles SQLAlchemy : companies, advertisements, people, applications
- [x] Relations, clés étrangères et suppression en cascade
- [x] MySQL/Aiven configurable ; SQLite pour le développement et les tests isolés
- [x] Initialisation explicite des tables via `python -m app.seed`
- [x] Données de démonstration créées par le backend (`--demo`)
- [x] Création explicite d'un administrateur, sans mot de passe prédéfini
- [x] Tables séparées pour les identifiants et les sessions
- [x] Requêtes SQL d'entraînement (`bootstrap-queries.sql`)
- [ ] Validation de l'intégration sur la base MySQL distante (non exécutée ici)

## 2. API

- [x] CRUD annonces, entreprises, personnes et candidatures
- [x] Route des annonces par entreprise
- [x] Candidature visiteur ou connecté, message conservé en base
- [x] Inscription, connexion, déconnexion et modification du compte
- [x] Contrôle des rôles côté serveur et sessions expirables/révocables
- [x] Mots de passe PBKDF2-SHA256 salés ; jetons stockés sous forme de hash
- [x] Masquage des annonces non publiées pour le public
- [x] Pagination, erreurs de validation, conflits et ressources absentes
- [x] CORS configurable et environnement local documenté
- [x] Tests API pytest et lint/format Ruff

## 3. Frontend

- [x] Liste paginée des annonces : titre, description courte, lieu, contrat, date
- [x] Détails complets obtenus par fetch, sans rechargement ni popup
- [x] Formulaire de candidature et confirmation après enregistrement
- [x] Coordonnées du compte utilisées automatiquement pour un candidat connecté
- [x] Pages d'inscription, connexion et modification du profil
- [x] Redirection selon le rôle après connexion
- [x] Administration protégée : listes, création, modification, suppression, pagination
- [x] Chargement, erreurs et actions de reprise
- [x] Conservation des composants existants et adaptation responsive des styles
- [x] ESLint et build Vite
- [x] Test Chromium de bout en bout, avec base et serveurs temporaires

## 4. Livraison

- [x] README : installation, configuration, lancement, schéma, routes et pages
- [x] Fichiers `.env.example` pour les deux applications
- [x] Tests locaux sans accès à Aiven
- [ ] Déploiement backend Render / frontend Vercel
- [ ] Validation fonctionnelle sur MySQL et environnement déployé

## 5. Limites / étapes suivantes

- [ ] Vérification d'email et récupération du mot de passe
- [ ] Conversion sécurisée d'une fiche visiteur existante en compte
- [ ] Limitation des tentatives de connexion avant ouverture publique
- [ ] Envoi réel d'emails (actuellement : stockage des messages en base)
- [ ] Import/scraping d'offres, si retenu par l'équipe

Une adresse déjà enregistrée ne peut pas être utilisée pour une candidature
anonyme : il faut se connecter, ou contacter l'administrateur si c'est une fiche
sans compte. Ce choix évite d'associer un visiteur à l'identité d'une autre personne.
Les catégories de l'exemple HireLoop ne sont pas exigées par le sujet final et
n'ont pas été ajoutées au schéma existant.
