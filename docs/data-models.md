# Data models

### `advertisements`

```js
const advertisement = {
  id: 0, // INT UNSIGNED, auto-incrémenté (clé primaire)
  title: "", // VARCHAR(150), obligatoire
  short_description: "", // VARCHAR(300), obligatoire
  full_description: "", // TEXT, obligatoire
  salary: null, // DECIMAL(10,2), facultatif, >= 0
  location: null, // VARCHAR(150), facultatif
  working_time: null, // VARCHAR(50), facultatif
  contract_type: null, // ENUM, facultatif : "cdi" | "cdd" | "alternance" | "stage" | "freelance" | "interim"
  status: "draft", // ENUM, obligatoire : "draft" | "published" | "archived" (défaut : "draft")
  company_id: 0, // INT UNSIGNED, obligatoire (clé étrangère -> companies.id, ON DELETE CASCADE)
  created_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, généré automatiquement (ISO 8601, UTC)
  updated_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, mis à jour automatiquement à chaque modification
};
```

### `applications`

```js
const application = {
  id: 0, // INT UNSIGNED, auto-incrémenté (clé primaire)
  people_id: 0, // INT UNSIGNED, obligatoire (clé étrangère -> people.id, ON DELETE CASCADE)
  advertisement_id: 0, // INT UNSIGNED, obligatoire (clé étrangère -> advertisements.id, ON DELETE CASCADE)
  message: "", // TEXT, obligatoire
  status: "pending", // ENUM, obligatoire : "pending" | "accepted" | "rejected" (défaut : "pending")
  created_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, généré automatiquement (ISO 8601, UTC)
  updated_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, mis à jour automatiquement à chaque modification
};
```

### `companies`

```js
const company = {
  id: 0, // INT UNSIGNED, auto-incrémenté (clé primaire)
  name: "", // VARCHAR(150), obligatoire, unique
  description: null, // TEXT, facultatif
  email: null, // VARCHAR(255), facultatif
  phone: null, // VARCHAR(20), facultatif
  address: null, // VARCHAR(255), facultatif
  city: null, // VARCHAR(100), facultatif
  country: null, // VARCHAR(100), facultatif
  created_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, généré automatiquement (ISO 8601, UTC)
  updated_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, mis à jour automatiquement à chaque modification
};
```

### `people`

```js
const people = {
  id: 0, // INT UNSIGNED, auto-incrémenté (clé primaire)
  firstname: "", // VARCHAR(50), obligatoire
  lastname: "", // VARCHAR(50), obligatoire
  email: "", // VARCHAR(255), obligatoire, unique
  phone: null, // VARCHAR(20), facultatif
  role: "user", // ENUM, obligatoire : "user" | "admin" (défaut : "user")
  created_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, généré automatiquement (ISO 8601, UTC)
  updated_at: "2026-10-08T16:28:45.000Z", // TIMESTAMP, mis à jour automatiquement à chaque modification
};
```
