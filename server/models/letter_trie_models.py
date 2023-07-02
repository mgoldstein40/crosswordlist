from flask import jsonify
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Text
)

from models.base_model import db


class LetterTrieDictionaries(db.Model):
    __tablename__ = "letter_trie_dictionaries"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    date = Column(Date)

    def __init__(self, json):
        self.from_json(json)
    
    def __repr__(self):
        return jsonify(self.to_json())


class LetterTrieWords(db.Model):
    __tablename__ = "letter_trie_words"

    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(Text, nullable=False)

    def __init__(self, json):
        self.from_json(json)
    
    def __repr__(self):
        return jsonify(self.to_json())


class LetterTrieDefinitions(db.Model):
    __tablename__ = "letter_trie_definitions"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("letter_trie_words.id"), nullable=False)
    dictionary_id = Column(Integer, ForeignKey("litter_trie_dictionaries.id"), nullable=False)
    text = Column(Text, nullable=False)

    def __init__(self, json):
        self.from_json(json)
    
    def __repr__(self):
        return jsonify(self.to_json())