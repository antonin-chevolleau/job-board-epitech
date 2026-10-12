export const resources = {
  advertisements: { label: 'Advertisements', action: 'New advertisement', fields: [
    ['title', 'Title', 'text', true, 150],
    ['short_description', 'Short description', 'textarea', true, 300],
    ['full_description', 'Full description', 'textarea', true],
    ['company_id', 'Company ID', 'id', true],
    ['salary', 'Salary (€)', 'number'], ['location', 'Location', 'text', false, 150],
    ['working_time', 'Working time', 'text', false, 50],
    ['contract_type', 'Contract', ['cdi', 'cdd', 'alternance', 'stage', 'freelance', 'interim']],
    ['status', 'Status', ['draft', 'published', 'archived'], true],
  ] },
  companies: { label: 'Companies', action: 'New company', fields: [
    ['name', 'Name', 'text', true, 150], ['description', 'Description', 'textarea'],
    ['email', 'Email', 'email', false, 255], ['phone', 'Phone', 'tel', false, 20],
    ['address', 'Address', 'text', false, 255], ['city', 'City', 'text', false, 100],
    ['country', 'Country', 'text', false, 100],
  ] },
  people: { label: 'People', action: 'New person', fields: [
    ['firstname', 'First name', 'text', true, 50], ['lastname', 'Last name', 'text', true, 50],
    ['email', 'Email', 'email', true, 255], ['phone', 'Phone', 'tel', false, 20],
  ] },
  applications: { label: 'Applications', action: 'New application', fields: [
    ['people_id', 'Person ID', 'id', true], ['advertisement_id', 'Advertisement ID', 'id', true],
    ['message', 'Message', 'textarea', true],
    ['status', 'Status', ['pending', 'accepted', 'rejected'], true],
  ] },
}
