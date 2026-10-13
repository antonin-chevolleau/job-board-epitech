export const resources = {
  advertisements: { label: 'Annonces', action: 'Nouvelle annonce', fields: [
    ['title', 'Titre', 'text', true, 150],
    ['short_description', 'Description courte', 'textarea', true, 300],
    ['full_description', 'Description complète', 'textarea', true, 10000],
    ['company_id', 'ID entreprise', 'id', true],
    ['salary', 'Salaire (€)', 'number'], ['location', 'Lieu', 'text', false, 150],
    ['working_time', 'Temps de travail', 'text', false, 50],
    ['contract_type', 'Contrat', ['CDI', 'CDD', 'Stage', 'Alternance', 'Freelance'], true],
    ['is_active', 'Active', ['true', 'false'], true],
  ] },
  companies: { label: 'Entreprises', action: 'Nouvelle entreprise', fields: [
    ['name', 'Nom', 'text', true, 150], ['description', 'Description', 'textarea', false, 10000],
    ['email', 'Email', 'email', true, 255], ['phone', 'Téléphone', 'tel', true, 20],
    ['address', 'Adresse', 'text', false, 255], ['city', 'Ville', 'text', true, 100],
    ['country', 'Pays', 'text', false, 100],
  ] },
  users: { label: 'Utilisateurs', action: 'Nouvel utilisateur', fields: [
    ['user_name', 'Nom d’utilisateur (sans @)', 'text', true, 50],
    ['first_name', 'Prénom', 'text', true, 100], ['last_name', 'Nom', 'text', true, 100],
    ['email', 'Email', 'email', true, 255], ['phone', 'Téléphone', 'tel', true, 20],
    ['role', 'Rôle', ['user', 'recruiter', 'admin'], true],
    ['company_id', 'ID entreprise', 'id'],
    ['password', 'Mot de passe (vide = inchangé)', 'password', false, 72],
  ] },
  applications: { label: 'Candidatures', action: 'Nouvelle candidature', fields: [
    ['advertisement_id', 'ID annonce', 'id', true],
    ['applicant_name', 'Nom du candidat', 'text', true, 200],
    ['applicant_email', 'Email du candidat', 'email', true, 255],
    ['applicant_phone', 'Téléphone du candidat', 'tel', true, 20],
    ['message', 'Message', 'textarea', true, 5000],
    ['status', 'Statut', ['pending', 'reviewed', 'accepted', 'rejected'], true],
  ] },
}
