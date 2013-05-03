import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://localhost/twitter")
SQLALCHEMY_DATABASE_URI = "postgresql://localhost/twitter" 
#SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'twitter.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
