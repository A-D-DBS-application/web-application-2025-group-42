class Config:
    SECRET_KEY = "your-secret-key"

    # Supabase Postgres connection string (werkschema)
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:supabase42!@db.cnoqicqyuapnbjcumaoq.supabase.co:5432/postgres"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False