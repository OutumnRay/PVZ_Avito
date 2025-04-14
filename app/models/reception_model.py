RECEPTION_TABLE = """
CREATE TABLE IF NOT EXISTS receptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date_time TIMESTAMP NOT NULL DEFAULT NOW(),
    pvz_id UUID REFERENCES pvz(id),
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'close'))
);
"""
