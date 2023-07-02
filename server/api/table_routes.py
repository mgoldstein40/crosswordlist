import re

from flask import abort, Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from models.base_model import db
from models.table_models import Definitions, Dictionaries, Words


tables_api = Blueprint("api", __name__)


RE_ALPHANUMERIC = "[A-Z0-9]"
RE_VOWELS = "[AEIOUY]"
RE_CONSONANTS = "[BCDFGHJKLMNPQRSTVWXYZ]"
RE_QUESTION = "{}\{1\}".format(RE_ALPHANUMERIC)
RE_ASTERISK = "{}*".format(RE_ALPHANUMERIC)
RE_AT = "{}\{1\}".format(RE_VOWELS)
RE_HASH = "{}\{1\}".format(RE_CONSONANTS)

def _clean_word(word):
    cleaned_word = re.sub('[\'"\s]', '', word).upper()
    if re.search('[^A-Z0-9]', word):
        raise ValueError("")
    return cleaned_word

def _pattern_to_regex(pattern):
    cleaned_pattern = re.sub('[\'"\s]', '', pattern).upper()
    if re.search('[^A-Z0-9@#?*\[\]]', cleaned_pattern):
        raise ValueError("") 
    
    regex_pattern = ""
    bracket_opened = False

    for c in cleaned_pattern:
        if bracket_opened:
            if c == "]":
                regex_pattern += ")"
                bracket_opened = False
            elif c == "@" or c == "#" or c == "?" or c == "*" or c == "[":
                raise ValueError("")
            else:
                regex_pattern += "{}|".format(c)
        elif c == "]":
            raise ValueError("")
        elif c == "@":
            regex_pattern += RE_AT
        elif c == "#":
            regex_pattern += RE_HASH
        elif c == "?":
            regex_pattern += RE_QUESTION
        elif c == "*":
            regex_pattern += RE_ASTERISK
        elif c == "[":
            regex_pattern += "("
            bracket_opened = True
        else:
            regex_pattern += c
    if bracket_opened:
        raise ValueError("")
    
    return regex_pattern


@tables_api.route("/dictionaries/", methods=["POST"])
@tables_api.route("/dictionaries/<int:id>", methods=["GET", "PUT", "DELETE"])
def dictionaries(id=None):
    try:
        data = {}
        if request.method == "POST" or request.method == "PUT":
            data = request.get_json(force=True)
            if "id" in data:
                del data["id"]

        if request.method == "POST":
            dictionary = Dictionaries(data)
            db.session.add(dictionary)
            db.session.commit()
            return jsonify(dictionary.to_json())
        
        dictionary = db.session.query(Dictionaries).get({"id": id})

        if request.method == "PUT":
            dictionary.from_json(data)
            db.session.add(dictionary)
            db.session.commit()
            
        elif request.method == "DELETE":
            db.session.delete(dictionary)
            db.session.commit()

        return jsonify(dictionary.to_json())    
    except SQLAlchemyError:
        abort(404)
    


@tables_api.route("/words/", methods=["POST"])
@tables_api.route("/words/<int:id>", methods=["GET", "PUT", "DELETED"])
def words(id=None):
    try:
        data = {}
        if request.method == "POST" or request.method == "PUT":
            data = request.get_json(force=True)

            text = data.get("text")
            if not text:
                abort(400)
            data["text"] = _clean_word(text)

            if "id" in data:
                del data["id"]

        if request.method == "POST":
            word = Words(data)
            db.session.add(word)
            db.session.commit()
            return jsonify(word.to_json())
        
        word = db.session.query(Words).get({"id": id})

        if request.method == "PUT":
            word.from_json(data)
            db.session.add(word)
            db.session.commit()
            
        elif request.method == "DELETE":
            db.session.delete(word)
            db.session.commit()

        return jsonify(word.to_json())    
    except SQLAlchemyError:
        abort(404)


@tables_api.route("/definitions/", methods=["POST"])
@tables_api.route("/definitions/<int:id>", methods=["GET", "PUT", "DELETE"])
def definitions(id=None):
    try:
        data = {}
        if request.method == "POST" or request.method == "PUT":
            data = request.get_json(force=True)
            if "id" in data:
                del data["id"]

        if request.method == "POST":
            definition = Definitions(data)
            db.session.add(definition)
            db.session.commit()
            return jsonify(definition.to_json())
        
        definition = db.session.query(Definitions).get({"id": id})

        if request.method == "PUT":
            definition.from_json(data)
            db.session.add(definition)
            db.session.commit()
            
        elif request.method == "DELETE":
            db.session.delete(definition)
            db.session.commit()

        return jsonify(definition.to_json())    
    except SQLAlchemyError:
        abort(404)


@tables_api.route("/words/<string:pattern>", methods=["GET"])
def lookup(pattern):
    try:
        regex_pattern = _pattern_to_regex(pattern)
    except ValueError as e:
        abort(404, e.args[0])
    
    words = (
        db.session.query(Words.text)
        .filter_by(Words.text.regexp_match(regex_pattern))
        .all()
    )
    return jsonify(words)


@tables_api.route("/bulk-dictionary-insert/", methods=["POST"])
def bulk_dictionary_insert():
    data = request.get_json(force=True)
    word_pairs = data.get("word_pairs")
    if not word_pairs:
        abort(400)
    
    if "id" in data:
        del data["id"]

    try:
        dictionary = Dictionaries(data)
        db.session.add(dictionary)
        db.session.commit()
        dictionary_id = dictionary.id
    except SQLAlchemyError:
        abort(400)
    
    illegal_words = []
    for word_text, definiton_text in word_pairs.items():
        try:
            clean_text = _clean_word(word_text)
        except ValueError:
            illegal_words.append(word_text)
            continue
        
        try:
            word = Words({"text": clean_text})
        except SQLAlchemyError:
            word = db.session.query(Words).get({"text": clean_text})
        db.session.add(word)

        definition = Definitions({
            "word_id": word.id,
            "dictionary_id": dictionary_id,
            "text": definiton_text
        })
        db.session.add(definition)
    db.session.commit()
