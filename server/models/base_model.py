from flask_sqlalchemy import Model, SQLAlchemy

class Base(Model):
    def from_json(self, json):
        for attr, value in json.items():
            if hasattr(self, attr):
                setattr(self, attr, value)

    def to_json(self, attrs):
        return {attr: getattr(self, attr) for attr in attrs}


db = SQLAlchemy(model_class=Base)