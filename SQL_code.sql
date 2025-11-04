-- Table: company
CREATE TABLE company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    founded_date DATE,
    description TEXT,
    country VARCHAR(100)
);

-- Table: user
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    company INT REFERENCES company(id) ON DELETE SET NULL
);

-- Table: requirement
CREATE TABLE requirement (
    requirement_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    created_by INT REFERENCES "user"(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: data_input
CREATE TABLE data_input (
    data_input_id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    analysis_id UUID NOT NULL,
    category VARCHAR(255),
    expected_profit FLOAT8,
    total_investment_cost FLOAT8,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    requirement_id INT REFERENCES requirement(requirement_id) ON DELETE CASCADE,
    time_to_market_days INT,
    time_to_business_days INT
);

-- Table: results
CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    roi_percentage FLOAT4,
    time_to_value_days INT,
    confidence_value FLOAT4,
    created_at DATE DEFAULT CURRENT_DATE,
    requirement_id INT REFERENCES requirement(requirement_id) ON DELETE CASCADE,
    data_input_id INT REFERENCES data_input(data_input_id) ON DELETE CASCADE
);

-- Optioneel: Indexen voor performantie
#CREATE INDEX idx_user_company ON "user"(company);
#CREATE INDEX idx_requirement_company ON requirement(company_id);
#CREATE INDEX idx_datainput_company ON data_input(company_id);
#CREATE INDEX idx_datainput_requirement ON data_input(requirement_id);
#CREATE INDEX idx_results_requirement ON results(requirement_id);
#CREATE INDEX idx_results_data_input ON results(data_input_id);
