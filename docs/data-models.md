# Data models

Source de vérité : `backend/sql/schemas.sql` (les modèles SQLAlchemy de
`backend/app/models/` le reflètent). Toutes les tables ont `id` (INT auto-incrémenté),
`created_at` et `updated_at` (TIMESTAMP gérés par MySQL).

## Relations

```
companies 1 ──< users                 (users.company_id, ON DELETE SET NULL)
companies 1 ──< advertisements        (ON DELETE CASCADE)
users     1 ──< advertisements        (advertisements.user_id = auteur, ON DELETE SET NULL)
advertisements 1 ──< job_applications (ON DELETE CASCADE)
users     1 ──< job_applications      (user_id nullable : candidature anonyme, ON DELETE SET NULL)
```

## `companies`

```js
const company = {
  id: 0,
  name: "", // VARCHAR(150), obligatoire, unique
  description: null, // TEXT, facultatif
  email: "", // VARCHAR(255), obligatoire, unique
  phone: "", // VARCHAR(20), obligatoire (3 caractères minimum)
  address: null, // VARCHAR(255), facultatif
  city: "", // VARCHAR(100), obligatoire
  country: null, // VARCHAR(100), facultatif
};
```

## `users`

```js
const user = {
  id: 0,
  user_name: "", // VARCHAR(50), obligatoire, unique, sans "@" (3 caractères minimum)
  hashed_password: "", // VARCHAR(255), bcrypt, jamais renvoyé par l'API
  first_name: "", // VARCHAR(100), obligatoire
  last_name: "", // VARCHAR(100), obligatoire
  email: "", // VARCHAR(255), obligatoire, unique
  phone: "", // VARCHAR(20), obligatoire (3 caractères minimum)
  role: "user", // ENUM : "user" | "recruiter" | "admin" (défaut : "user")
  company_id: null, // INT, facultatif -> companies.id
};
```

## `advertisements`

```js
const advertisement = {
  id: 0,
  company_id: 0, // INT, obligatoire -> companies.id
  user_id: null, // INT, facultatif -> users.id (auteur ; l'admin courant par défaut à la création)
  title: "", // VARCHAR(150), obligatoire
  short_description: "", // VARCHAR(300), obligatoire
  full_description: "", // TEXT, obligatoire (10 000 caractères max côté API)
  location: null, // VARCHAR(150), facultatif
  salary: null, // DECIMAL(10,2), facultatif, >= 0
  contract_type: "CDI", // ENUM, obligatoire : "CDI" | "CDD" | "Stage" | "Alternance" | "Freelance"
  working_time: null, // VARCHAR(50), facultatif
  is_active: true, // BOOLEAN ; les annonces inactives ne sont visibles que par l'admin
};
```

## `job_applications`

```js
const jobApplication = {
  id: 0,
  advertisement_id: 0, // INT, obligatoire -> advertisements.id
  user_id: null, // INT, facultatif -> users.id (null = visiteur anonyme)
  applicant_name: "", // VARCHAR(200), obligatoire
  applicant_email: "", // VARCHAR(255), obligatoire
  applicant_phone: "", // VARCHAR(20), obligatoire (3 caractères minimum)
  message: "", // TEXT, obligatoire (5 000 caractères max côté API)
  status: "pending", // ENUM : "pending" | "reviewed" | "accepted" | "rejected"
  email_sent_at: null, // TIMESTAMP, date d'envoi de la notification au recruteur
};
```

Unicité : (`advertisement_id`, `applicant_email`). Un utilisateur connecté postule
toujours avec l'email de son compte ; un visiteur ne peut pas utiliser l'email d'un compte.
