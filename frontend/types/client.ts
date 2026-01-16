export interface ClientAutomobile {
    id: string;
    client_id: string;
    vehicle_registration?: string;
    vehicle_make?: string;
    vehicle_model?: string;
    vehicle_year?: number;
    vehicle_value?: number;
    vehicle_mileage?: number;
    engine_capacity_cc?: number;
    fuel_type?: string;
    vehicle_usage?: string;
    seat_count?: number;
    chassis_number?: string;
    vehicle_color?: string;
    country_of_registration?: string;
    driver_first_name?: string;
    driver_last_name?: string;
    driver_dob?: string;
    license_number?: string;
    license_issue_date?: string;
    license_expiry_date?: string;
    license_category?: string;
    driving_experience_years?: number;
    accident_count?: number;
    claim_count?: number;
    no_claim_bonus_status?: string;
    previous_insurer?: string;
    created_at: string;
    updated_at: string;
}

export interface ClientHousing {
    id: string;
    client_id: string;
    property_type?: string;
    address?: string;
    city?: string;
    country?: string;
    construction_year?: number;
    property_size_sqm?: number;
    room_count?: number;
    floor_count?: number;
    building_material?: string;
    occupancy_type?: string;
    building_value?: number;
    contents_value?: number;
    security_system: boolean;
    fire_protection: boolean;
    flood_zone: boolean;
    earthquake_zone: boolean;
    ownership_status?: string;
    mortgage_info?: string;
    created_at: string;
    updated_at: string;
}

export interface ClientHealth {
    id: string;
    client_id: string;
    height_cm?: number;
    weight_kg?: number;
    bmi?: number;
    blood_group?: string;
    smoking_status?: string;
    alcohol_consumption?: string;
    pre_existing_conditions?: string;
    chronic_diseases?: string;
    past_surgeries?: string;
    current_medications?: string;
    family_medical_history?: string;
    coverage_type?: string;
    dependents_list?: string;
    maternity_coverage: boolean;
    dental_optical_coverage: boolean;
    created_at: string;
    updated_at: string;
}

export interface ClientLife {
    id: string;
    client_id: string;
    dependent_count: number;
    annual_income?: number;
    source_of_income?: string;
    smoking_status?: string;
    alcohol_consumption?: string;
    high_risk_activities?: string;
    medical_history_summary?: string;
    beneficiaries?: string;
    created_at: string;
    updated_at: string;
}

export interface ClientDriver {
    id: string;
    client_id: string;
    first_name?: string;
    last_name?: string;
    phone_number: string;
    address: string;
    city?: string;
    postal_code?: string;
    country?: string;
    license_number: string;
    license_issue_date: string;
    employment_status: string;
    marital_status: string;
    number_of_children: number;
    photo_url?: string;
    is_main_driver: boolean;
    license_type?: string;
    cars_in_household?: number;
    residential_status?: string;
    accident_count?: number;
    no_claims_years?: number;
    driving_license_years?: number;
    driving_license_url?: string;
    created_at: string;
    updated_at: string;
}

export interface Client {
    id: string;
    company_id: string;
    user_id?: string;
    client_type: 'individual' | 'corporate';
    status: string;

    // Basic Info
    first_name?: string;
    last_name?: string;
    business_name?: string;
    email: string;
    phone: string;
    phone_number?: string;
    date_of_birth?: string;
    gender?: string;
    address?: string;
    city?: string;
    country: string;
    profile_picture?: string;

    // Identity
    nationality?: string;
    id_number?: string;
    id_expiry_date?: string;
    id_card_url?: string;
    passport_url?: string;
    marital_status?: string;

    // Professional
    occupation?: string;
    employer_name?: string;
    employment_status?: string;
    annual_income?: number;

    // Compliance
    kyc_status: string;
    kyc_notes?: string;
    kyc_results?: any;
    pep_status: boolean;
    consent_accepted: boolean;

    driving_licence_number?: string;
    driving_license_url?: string;
    tax_id?: string;
    risk_profile: string;

    // Eligibility
    accident_count?: number;
    no_claims_years?: number;
    driving_license_years?: number;

    created_at: string;
    updated_at: string;

    // Details (Optional/Loaded if requested)
    automobile_details?: ClientAutomobile[];
    drivers?: ClientDriver[];
    housing_details?: ClientHousing;
    health_details?: ClientHealth;
    life_details?: ClientLife;
}
