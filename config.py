class Config:
    # ...existing code...
    SECRET_KEY = "your-secret-key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password@localhost/final_project_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # ...existing code...
