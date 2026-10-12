-- Requêtes d'entraînement du bootstrap, adaptées au schéma final existant.
-- Compatibles SQLite / MySQL. Données de démonstration : python -m app.seed --demo.

-- Nombre d'annonces par entreprise, y compris les entreprises sans annonce.
SELECT c.id, c.name, COUNT(a.id) AS advertisement_count
FROM companies AS c
LEFT JOIN advertisements AS a ON a.company_id = c.id
GROUP BY c.id, c.name
ORDER BY advertisement_count DESC;

-- Annonce ayant reçu le plus de candidatures.
SELECT a.id, a.title, COUNT(ap.id) AS application_count
FROM advertisements AS a
LEFT JOIN applications AS ap ON ap.advertisement_id = a.id
GROUP BY a.id, a.title
ORDER BY application_count DESC, a.id
LIMIT 1;

-- Candidats pour l'annonce 1 avec leur message et leur date.
SELECT p.firstname, p.lastname, p.email, ap.message, ap.created_at
FROM applications AS ap
JOIN people AS p ON p.id = ap.people_id
JOIN advertisements AS a ON a.id = ap.advertisement_id
WHERE a.id = 1
ORDER BY ap.created_at;
