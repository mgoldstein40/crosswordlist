from flask import abort, Blueprint, jsonify, request

from models.base_model import db
from models.trie_models import TrieDefinitions, TrieDictionaries, TrieWords


api = Blueprint("api", __name__)