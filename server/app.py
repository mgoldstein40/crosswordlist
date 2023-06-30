from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://{}:{}@{}/{}".format(
    db_user, db_password, db_host, db_name
)


db.init_app(app)