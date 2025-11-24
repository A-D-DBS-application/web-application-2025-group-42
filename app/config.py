class Config:
    SECRET_KEY = "changeme-but-keep-it-long"  # mag je zelf aanpassen
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:supabase42!@db.cnoqicqyuapnbjcumaoq.supabase.co:5432/postgres?sslmode=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
