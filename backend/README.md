# Job Board | Backend

REST API of the Job Board project (see `../sujets/jobBoard-project.pdf`): job advertisements, companies,
users, authentication and job applications, stored in MySQL.

Stack: **Python 3.12+**, **FastAPI**, **SQLAlchemy 2**, **MySQL 8**, JWT (PyJWT) and bcrypt.

## Installation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt        # add requirements-dev.txt to run the tests
```

## Configuration

### 1. Database

Create an empty database, then load the schema and the seed data:

```bash
mysql -u <user> -p -e "CREATE DATABASE job_board CHARACTER SET utf8mb4;"
mysql -u <user> -p job_board < sql/schemas.sql   # WARNING: drops and recreates all tables
mysql -u <user> -p job_board < sql/seed.sql      # optional: demo data
```

Seeded accounts (password `admin1234` for all of them, **change it outside development**):

| user_name   | role        | notes                      |
| ----------- | ----------- | -------------------------- |
| `admin`     | `admin`     | access to the admin routes |
| `recruiter` | `recruiter` | posts the Acme Tech ads    |
| `jdoe`      | `user`      | regular candidate          |

### 2. Environment

```bash
cp .env.example .env
```

| Variable                          | Required | Description                                                                         |
| --------------------------------- | -------- | ----------------------------------------------------------------------------------- |
| `DATABASE_URL`                    | yes      | `mysql+pymysql://USER:PASSWORD@localhost:3306/job_board`                            |
| `SECRET_KEY`                      | yes      | JWT signing key, at least 32 characters; the `.env.example` placeholder is rejected |
| `ACCESS_TOKEN_EXPIRE_MINUTES`     | no       | Token lifetime, default `60`                                                        |
| `CORS_ORIGINS`                    | no       | Comma-separated front-end origins, default: Vite on port 5173                |
| `RATE_LIMIT_ENABLED`              | no       | Default `true`                                                                      |
| `RATE_LIMIT_LOGIN`                | no       | Login attempts per client IP, default `10/minute`                                   |
| `RATE_LIMIT_APPLY`                | no       | Applications per client IP, default `20/hour`                                       |
| `SMTP_HOST`                       | no       | Enables the email sent to the ad owner on each application                          |
| `SMTP_PORT`                       | no       | Default `587`                                                                       |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | no       | SMTP credentials                                                                    |
| `SMTP_FROM`                       | no       | Sender address, default `noreply@jobboard.local`                                    |
| `SMTP_STARTTLS`                   | no       | Default `true`                                                                      |

Generate a key with `python3 -c "import secrets; print(secrets.token_hex(32))"`.
`.env` is git-ignored: never commit real credentials.

## Run

```bash
.venv/bin/uvicorn app.main:app --reload
```

- API: <http://localhost:8000/api>
- Interactive documentation (Swagger): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

## Tests

```bash
.venv/bin/pytest
```

The tests run against the database configured in `.env` (seeded with `sql/seed.sql`, they log in as
`admin` / `admin1234`). Every test deletes the records it creates.

## Project layout

```bash
.
|--- sql/
|    |--- schemas.sql # database schema (source of truth, drops existing tables)
|    |--- seed.sql # demo data
|--- app/
|    |--- main.py # FastAPI app, CORS, /health
|    |--- core/ # config.py (settings from .env), database.py (engine, session), security.py (bcrypt, JWT), rate_limit.py (sliding window)
|    |--- models/ # SQLAlchemy models, one file per table (mirror sql/schemas.sql)
|    |--- schemas/ # Pydantic request / response models, one file per resource (+ common, auth)
|    |--- api/
|    |    |--- router.py #  mounts all routes under /api
|    |    |--- deps.py #  dependencies: DB session, current user, admin check
|    |    |--- pagination.py #  page / limit query parameters and paginate()
|    |    |--- rate_limit.py #  per-IP rate limit dependencies (login, application)
|    |    |--- errors.py #  get_or_404 and MySQL integrity errors mapped to HTTP errors
|    |    |--- routes/ #  auth, companies, advertisements, users, applications
|    |--- services/
|    |    |--- emailer.py # optional SMTP notification for applications
|--- tests/ # pytest API tests (run against the database of .env)
```

## Database schema

```
companies 1 ──< users                 (users.company_id, ON DELETE SET NULL)
companies 1 ──< advertisements        (ON DELETE CASCADE)
users     1 ──< advertisements        (advertisements.user_id = poster, ON DELETE SET NULL)
advertisements 1 ──< job_applications (ON DELETE CASCADE)
users     1 ──< job_applications      (job_applications.user_id, nullable: anonymous, ON DELETE SET NULL)
```

| Table              | Main columns                                                                                                                                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `companies`        | `name` (unique), `description`, `email` (unique), `phone`, `address`, `city`, `country`                                                                                                                                  |
| `users`            | `user_name` (unique), `hashed_password`, `first_name`, `last_name`, `email` (unique), `phone`, `role` (`user`/`recruiter`/`admin`), `company_id`                                                                         |
| `advertisements`   | `company_id`, `user_id`, `title`, `short_description`, `full_description`, `location`, `salary`, `contract_type` (`CDI`/`CDD`/`Stage`/`Alternance`/`Freelance`), `working_time`, `is_active`                             |
| `job_applications` | `advertisement_id`, `user_id`, `applicant_name`, `applicant_email`, `applicant_phone`, `message`, `status` (`pending`/`reviewed`/`accepted`/`rejected`), `email_sent_at`; unique (`advertisement_id`, `applicant_email`) |

Every table also has `id`, `created_at` and `updated_at`.

## API

All routes are prefixed with `/api`. Authenticated routes expect `Authorization: Bearer <token>`.

### Conventions

- **Pagination**: list routes accept `page` (default `1`) and `limit` (default `20`, max `100`) and
  return `{ "items": [...], "total": 42, "page": 1, "limit": 20 }`.
- **Update**: `PUT` replaces the whole resource: every field must be sent, optional ones as `null`
  (omitting a field is a `422`, nothing is reset silently). The only exception is `password` on
  `PUT /users/{id}`, which is left unchanged when omitted.
- **Rate limiting**: `POST /api/auth/login` and `POST /api/advertisements/{id}/applications` are limited
  per client IP (`RATE_LIMIT_LOGIN`, `RATE_LIMIT_APPLY`); every attempt counts, successful or not. Beyond
  the limit the API answers `429` with a `Retry-After` header (seconds). Counters live in the process
  memory: with several workers each one counts on its own. Behind a reverse proxy, run uvicorn with
  `--forwarded-allow-ips=<proxy ip>` so the real client IP is used instead of the proxy's.
- **Tokens**: an invalid or expired token is treated as "not logged in": public routes keep working,
  protected routes answer `401`.
- **Deletion**: `204 No Content`.
- **Errors**: `401` not authenticated, `403` not an admin, `404` not found, `429` too many requests, `409` duplicate value or
  record still referenced, `422` invalid body (too long, out of range, missing field) or reference to a missing record.

### Authentication

| Method | Route                | Access    | Description                                                                                           |
| ------ | -------------------- | --------- | ----------------------------------------------------------------------------------------------------- |
| POST   | `/api/auth/register` | public    | Create a `user` account (`user_name` cannot contain `@`)                                               |
| POST   | `/api/auth/login`    | public    | Form fields `username` (user name or email) and `password`; returns `access_token`, `role`, `user_id` |
| GET    | `/api/auth/me`       | logged in | Current profile                                                                                       |
| PUT    | `/api/auth/me`       | logged in | Update the profile; `new_password` requires `current_password`                                        |

The front end redirects to the administration page when the returned `role` is `admin`.

### Advertisements

| Method | Route                                   | Access              | Description                                                                                                                                     |
| ------ | --------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/advertisements`                   | public              | List (without `full_description`). Filters: `q` (title, short description), `location`, `contract_type`, `company_id`, `is_active` (admin only) |
| GET    | `/api/advertisements/{id}`              | public              | Full detail, used by the "Learn more" button                                                                                                    |
| POST   | `/api/advertisements/{id}/applications` | public or logged in | Apply to an advertisement (see below)                                                                                                           |
| POST   | `/api/advertisements`                   | admin               | Create (`user_id` defaults to the current admin)                                                                                                |
| PUT    | `/api/advertisements/{id}`              | admin               | Update                                                                                                                                          |
| DELETE | `/api/advertisements/{id}`              | admin               | Delete, with its applications                                                                                                                   |

Inactive advertisements are only visible to admins (others get `404`).

**Applying**: the body is `{ "message": "...", "applicant_name": "...", "applicant_email": "...", "applicant_phone": "..." }`.
Logged-in users only need `message`: name and phone default to their profile and the email is always the
one of their account (a submitted `applicant_email` is ignored). Anonymous visitors must provide the three
identity fields and cannot use the email of an existing account (`409`, they must log in). One application
per email and advertisement, and one per logged-in user and advertisement (`409`). When `SMTP_HOST` is set, the ad owner (the poster, otherwise
the company) is emailed in the background and `email_sent_at` is recorded.

### Companies

| Method | Route                 | Access | Description                                            |
| ------ | --------------------- | ------ | ------------------------------------------------------ |
| GET    | `/api/companies`      | public | List; filter `q` (name, city)                          |
| GET    | `/api/companies/{id}` | public | Detail                                                 |
| POST   | `/api/companies`      | admin  | Create                                                 |
| PUT    | `/api/companies/{id}` | admin  | Update                                                 |
| DELETE | `/api/companies/{id}` | admin  | Delete, with its advertisements and their applications |

### Users (admin only)

| Method | Route             | Description                                                               |
| ------ | ----------------- | ------------------------------------------------------------------------- |
| GET    | `/api/users`      | List; filters `q` (user name, names, email), `role`, `company_id`         |
| GET    | `/api/users/{id}` | Detail                                                                    |
| POST   | `/api/users`      | Create (any role, `password` required, 8 to 72 characters)                |
| PUT    | `/api/users/{id}` | Update; omit `password` to keep the current one                           |
| DELETE | `/api/users/{id}` | Delete (an admin cannot delete themselves or remove their own admin role) |

### Applications (admin only)

| Method | Route                    | Description                                                              |
| ------ | ------------------------ | ------------------------------------------------------------------------ |
| GET    | `/api/applications`      | List; filters `q` (name, email), `advertisement_id`, `user_id`, `status` |
| GET    | `/api/applications/{id}` | Detail                                                                   |
| POST   | `/api/applications`      | Create                                                                   |
| PUT    | `/api/applications/{id}` | Update (e.g. change the `status`)                                        |
| DELETE | `/api/applications/{id}` | Delete                                                                   |

## Pages

The web pages (job board, authentication, administration) belong to the front end, which only talks to
this API. This backend serves no HTML.

| Page           | Routes used                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------- |
| Job board      | `GET /advertisements`, `GET /advertisements/{id}` ("Learn more"), `POST /advertisements/{id}/applications` ("Apply") |
| Sign in / up   | `POST /auth/login`, `POST /auth/register`, `GET` and `PUT /auth/me`                                                  |
| Administration | CRUD on `/companies`, `/advertisements`, `/users`, `/applications` (paginated lists)                                 |
