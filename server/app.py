from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from models.base_model import db
from api.table_routes import tables_api


app = Flask(__name__)

app.config.from_pyfile("flask.cfg")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{}:{}@{}/{}".format(
    app.config.get("DB_USER"),
    app.config.get("DB_PASSWORD"),
    app.config.get("DB_HOST"),
    app.config.get("DB_DATABASE")
)

db.init_app(app)
app.register_blueprint(tables_api, url_prefix="/api")


if __name__ == "__main__":
    app.run(debug=True)