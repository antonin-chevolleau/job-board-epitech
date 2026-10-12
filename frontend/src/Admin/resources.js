// Fields exposed by the API; IDs/timestamps are read-only in the table.
export const resources = {
  advertisements: { label: 'Annonces', fields: [
    ['title', 'Titre', 'text', true, 150],
    ['short_description', 'Description courte', 'textarea', true, 300],
    ['full_description', 'Description complète', 'textarea', true],
    ['company_id', 'ID entreprise', 'id', true],
    ['salary', 'Salaire (€)', 'number'], ['location', 'Lieu', 'text', false, 150],
    ['working_time', 'Temps de travail', 'text', false, 50],
    ['contract_type', 'Contrat', ['cdi', 'cdd', 'alternance', 'stage', 'freelance', 'interim']],
    ['status', 'Statut', ['draft', 'published', 'archived'], true],
  ] },
  companies: { label: 'Entreprises', fields: [
    ['name', 'Nom', 'text', true, 150], ['description', 'Description', 'textarea'],
    ['email', 'Email', 'email', false, 255], ['phone', 'Téléphone', 'tel', false, 20],
    ['address', 'Adresse', 'text', false, 255], ['city', 'Ville', 'text', false, 100],
    ['country', 'Pays', 'text', false, 100],
  ] },
  people: { label: 'Personnes', fields: [
    ['firstname', 'Prénom', 'text', true, 50], ['lastname', 'Nom', 'text', true, 50],
    ['email', 'Email', 'email', true, 255], ['phone', 'Téléphone', 'tel', false, 20],
  ] },
  applications: { label: 'Candidatures', fields: [
    ['people_id', 'ID personne', 'id', true], ['advertisement_id', 'ID annonce', 'id', true],
    ['message', 'Message', 'textarea', true],
    ['status', 'Statut', ['pending', 'accepted', 'rejected'], true],
  ] },
}
