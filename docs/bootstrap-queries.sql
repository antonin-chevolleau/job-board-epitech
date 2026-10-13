-- Requêtes d'entraînement du bootstrap, adaptées au schéma backend/sql/schemas.sql.
-- Données de démonstration : backend/sql/seed.sql.

-- Nombre d'annonces par entreprise, y compris les entreprises sans annonce.
SELECT c.id, c.name, COUNT(a.id) AS advertisement_count
FROM companies AS c
LEFT JOIN advertisements AS a ON a.company_id = c.id
GROUP BY c.id, c.name
ORDER BY advertisement_count DESC;

-- Annonce ayant reçu le plus de candidatures.
SELECT a.id, a.title, COUNT(ja.id) AS application_count
FROM advertisements AS a
LEFT JOIN job_applications AS ja ON ja.advertisement_id = a.id
GROUP BY a.id, a.title
ORDER BY application_count DESC, a.id
LIMIT 1;

-- Candidats pour l'annonce 1 avec leur message et leur date
-- (user_name est NULL pour une candidature anonyme).
SELECT ja.applicant_name, ja.applicant_email, u.user_name, ja.message, ja.created_at
FROM job_applications AS ja
LEFT JOIN users AS u ON u.id = ja.user_id
WHERE ja.advertisement_id = 1
ORDER BY ja.created_at;
