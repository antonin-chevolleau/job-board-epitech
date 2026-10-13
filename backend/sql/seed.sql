-- Dev seed data. Run after schemas.sql.
-- Default password for every seeded user: admin1234
INSERT INTO
  companies (
    name,
    description,
    email,
    phone,
    address,
    city,
    country
  )
VALUES
  (
    'Acme Tech',
    'Software studio building web and mobile products.',
    'jobs@acme-tech.example',
    '+33140000001',
    '12 rue de la Paix',
    'Paris',
    'France'
  ),
  (
    'Green Logistics',
    'Sustainable transport and delivery solutions.',
    'hr@green-logistics.example',
    '+33470000002',
    '5 quai du Rhône',
    'Lyon',
    'France'
  ),
  (
    'Pixel Studio',
    'Independent game and motion design studio.',
    'hello@pixel-studio.example',
    '+33560000003',
    '8 allée Jean Jaurès',
    'Toulouse',
    'France'
  );

INSERT INTO
  users (
    user_name,
    hashed_password,
    first_name,
    last_name,
    email,
    phone,
    role,
    company_id
  )
VALUES
  (
    'admin',
    '$2b$12$dW/7iYHfIZtvOi9jErbk6ekpVr3IoDtLIzQuZGj/z/iWj5hlJUpFS',
    'Admin',
    'Root',
    'admin@jobboard.example',
    '+33600000000',
    'admin',
    NULL
  ),
  (
    'recruiter',
    '$2b$12$dW/7iYHfIZtvOi9jErbk6ekpVr3IoDtLIzQuZGj/z/iWj5hlJUpFS',
    'Claire',
    'Martin',
    'claire.martin@acme-tech.example',
    '+33600000001',
    'recruiter',
    1
  ),
  (
    'jdoe',
    '$2b$12$dW/7iYHfIZtvOi9jErbk6ekpVr3IoDtLIzQuZGj/z/iWj5hlJUpFS',
    'John',
    'Doe',
    'john.doe@example.com',
    '+33600000002',
    'user',
    NULL
  );

INSERT INTO
  advertisements (
    company_id,
    user_id,
    title,
    short_description,
    full_description,
    location,
    salary,
    contract_type,
    working_time,
    is_active
  )
VALUES
  (
    1,
    2,
    'Développeur Full-Stack',
    'Rejoignez notre équipe produit sur une stack JS/Python.',
    'Vous concevez et développez des fonctionnalités web de bout en bout (React, FastAPI, MySQL), en lien avec les équipes design et produit.',
    'Paris',
    42000.00,
    'CDI',
    '35h',
    TRUE
  ),
  (
    1,
    2,
    'Stage Développeur Backend',
    'Stage de 6 mois autour d''API REST en Python.',
    'Vous participez à la conception d''API REST, à l''écriture de tests et à la mise en production avec l''équipe backend.',
    'Paris',
    1200.00,
    'Stage',
    '35h',
    TRUE
  ),
  (
    2,
    NULL,
    'Data Analyst',
    'Analysez les flux de livraison pour optimiser les tournées.',
    'Vous exploitez les données de transport (SQL, Python) pour produire des tableaux de bord et des recommandations.',
    'Lyon',
    38000.00,
    'CDD',
    '35h',
    TRUE
  ),
  (
    3,
    NULL,
    'Motion Designer',
    'Créez des animations pour nos jeux et nos clients.',
    'Vous réalisez des animations 2D/3D et des trailers, en collaboration avec les directeurs artistiques.',
    'Toulouse',
    NULL,
    'Freelance',
    'Temps partiel',
    TRUE
  ),
  (
    3,
    NULL,
    'Alternance Intégrateur Web',
    'Alternance en intégration HTML/CSS/JS.',
    'Vous intégrez des maquettes et participez à l''amélioration continue de nos sites vitrines.',
    'Toulouse',
    900.00,
    'Alternance',
    '35h',
    FALSE
  );

INSERT INTO
  job_applications (
    advertisement_id,
    user_id,
    applicant_name,
    applicant_email,
    applicant_phone,
    message,
    status
  )
VALUES
  (
    1,
    3,
    'John Doe',
    'john.doe@example.com',
    '+33600000002',
    'Bonjour, votre offre m''intéresse beaucoup.',
    'pending'
  ),
  (
    3,
    NULL,
    'Alice Durand',
    'alice.durand@example.com',
    '+33600000010',
    'Disponible dès le mois prochain.',
    'reviewed'
  );