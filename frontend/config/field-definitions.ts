
export interface FieldOption {
    value: string;
    label: string;
}

export interface FieldDefinition {
    key: string;
    label: string;
    type: 'text' | 'number' | 'date' | 'select' | 'file';
    options?: FieldOption[];
    required?: boolean;
    section?: string;
}

export const MARITAL_STATUS_OPTIONS: FieldOption[] = [
    { value: 'single', label: 'Single' },
    { value: 'married', label: 'Married' },
    { value: 'divorced', label: 'Divorced' },
    { value: 'widowed', label: 'Widowed' }
];

export const EMPLOYMENT_STATUS_OPTIONS: FieldOption[] = [
    { value: 'employed', label: 'Employed' },
    { value: 'self_employed', label: 'Self-Employed' },
    { value: 'unemployed', label: 'Unemployed' },
    { value: 'retired', label: 'Retired' },
    { value: 'student', label: 'Student' }
];

export const RESIDENTIAL_STATUS_OPTIONS: FieldOption[] = [
    { value: 'homeowner', label: 'Homeowner' },
    { value: 'tenant', label: 'Tenant' },
    { value: 'living_with_parents', label: 'Living with Parents' }
];

export const LICENSE_TYPE_OPTIONS: FieldOption[] = [
    { value: 'full', label: 'Full' },
    { value: 'provisional', label: 'Provisional' },
    { value: 'international', label: 'International' }
];

export const CLIENT_TYPE_OPTIONS: FieldOption[] = [
    { value: 'individual', label: 'Individual' },
    { value: 'corporate', label: 'Corporate' }
];

export const FUEL_TYPE_OPTIONS: FieldOption[] = [
    { value: 'petrol', label: 'Petrol' },
    { value: 'diesel', label: 'Diesel' },
    { value: 'electric', label: 'Electric' },
    { value: 'hybrid', label: 'Hybrid' }
];

export const VEHICLE_USAGE_OPTIONS: FieldOption[] = [
    { value: 'private', label: 'Private' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'taxi', label: 'Taxi' },
    { value: 'delivery', label: 'Delivery' }
];

// MUST strictly follow the order and requirements from User Request
export const UNIFIED_ENTITY_FIELDS: FieldDefinition[] = [
    { key: 'last_name', label: 'Name', type: 'text', required: true, section: 'Identity' },
    { key: 'first_name', label: 'Forenames', type: 'text', required: true, section: 'Identity' },
    { key: 'phone_number', label: 'Phone Number', type: 'text', required: true, section: 'Contact' },
    { key: 'date_of_birth', label: 'Date of Birth', type: 'date', required: true, section: 'Identity' },
    { key: 'address', label: 'Address', type: 'text', required: true, section: 'Address' },
    { key: 'city', label: 'City', type: 'text', required: true, section: 'Address' },
    { key: 'postal_code', label: 'Postal Code', type: 'text', section: 'Address' },
    { key: 'country', label: 'Country', type: 'text', required: true, section: 'Address' },
    { key: 'marital_status', label: 'Marital Status', type: 'select', options: MARITAL_STATUS_OPTIONS, section: 'Personal' },
    { key: 'employment_status', label: 'Employment Status', type: 'select', options: EMPLOYMENT_STATUS_OPTIONS, section: 'Personal' },
    { key: 'number_of_children', label: 'Number of Children', type: 'number', section: 'Personal' },
    { key: 'residential_status', label: 'Residential Status', type: 'select', options: RESIDENTIAL_STATUS_OPTIONS, section: 'Address' },
    { key: 'license_number', label: 'Driving Licence Number', type: 'text', section: 'License' },
    { key: 'license_type', label: 'Licence Type', type: 'select', options: LICENSE_TYPE_OPTIONS, section: 'License' },
    { key: 'license_issue_date', label: 'Licence Issue Date', type: 'date', section: 'License' },
    { key: 'driving_license_years', label: 'Licence Duration (years)', type: 'number', section: 'License' },
    { key: 'cars_in_household', label: 'Cars in Household', type: 'number', section: 'Auto' },
    { key: 'accident_count', label: 'Accidents (last 5 years)', type: 'number', section: 'History' },
    { key: 'no_claims_years', label: 'No Claims Discount (years)', type: 'number', section: 'History' },
    { key: 'driving_license_url', label: 'Upload Driving Licence', type: 'file', section: 'Documents' }
];

// Administrative fields required for backend Client creation but not in the "Unified 20"
export const CLIENT_ADMIN_FIELDS: FieldDefinition[] = [
    { key: 'client_type', label: 'Client Type', type: 'select', options: CLIENT_TYPE_OPTIONS, required: true, section: 'Profile' },
    { key: 'email', label: 'Email Address', type: 'text', required: true, section: 'Contact' },
    { key: 'business_name', label: 'Business Name', type: 'text', section: 'Identity' }
];

export const VEHICLE_FIELDS: FieldDefinition[] = [
    { key: 'vehicle_registration', label: 'Registration Number', type: 'text', required: true, section: 'Vehicle' },
    { key: 'vehicle_make', label: 'Make', type: 'text', required: true, section: 'Vehicle' },
    { key: 'vehicle_model', label: 'Model', type: 'text', required: true, section: 'Vehicle' },
    { key: 'vehicle_year', label: 'Year', type: 'number', section: 'Vehicle' },
    { key: 'vehicle_value', label: 'Vehicle Value', type: 'number', section: 'Vehicle' },
    { key: 'vehicle_usage', label: 'Usage', type: 'select', options: VEHICLE_USAGE_OPTIONS, section: 'Usage' },
    { key: 'vehicle_mileage', label: 'Annual Mileage', type: 'number', section: 'Usage' },
    { key: 'fuel_type', label: 'Fuel Type', type: 'select', options: FUEL_TYPE_OPTIONS, section: 'Vehicle' },
    { key: 'engine_capacity_cc', label: 'Engine CC', type: 'number', section: 'Vehicle' },
    { key: 'seat_count', label: 'Seat Count', type: 'number', section: 'Vehicle' },
    { key: 'vehicle_color', label: 'Color', type: 'text', section: 'Vehicle' },
    { key: 'parked_location', label: 'Overnight Parking', type: 'text', section: 'Usage' },
    { key: 'vehicle_image_url', label: 'Vehicle Photo', type: 'file', section: 'Documents' }
];

// Kept for backward compatibility during transition if needed, but UNIFIED_ENTITY_FIELDS is the new standard
export const SHARED_DRIVER_FIELDS = UNIFIED_ENTITY_FIELDS;
export const CLIENT_FORM_FIELDS = [...UNIFIED_ENTITY_FIELDS.filter(f => f.key !== 'driving_license_url'), ...CLIENT_ADMIN_FIELDS];
