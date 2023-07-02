from flask import jsonify
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Text
)

from models.base_model import db


class Dictionaries(db.Model):
    __tablename__ = "dictionaries"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    date = Column(Date)

    def __init__(self, json):
        self.from_json(json)
    
    def __repr__(self):
        return jsonify(self.to_json())


class Words(db.Model):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(Text, nullable=False)

    def __init__(self, json):
        self.from_json(json)
    
    def __repr__(self):
        return jsonify(self.to_json())


class Definitions(db.Model):
    __tablename__ = "definitions"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    dictionary_id = Column(Integer, ForeignKey("dictionaries.id"), nullable=False)
    text = Column(Text, nullable=False)

    def __init__(self, json):
        self.from_json(json)
    
    def __repr__(self):
        return jsonify(self.to_json())