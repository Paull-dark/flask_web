from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db.27017")
db = client.SimilarityDB
users = db["Users"]


def UserExist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True


class Register(Resource):

    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExist(username):
            retJson = {"status": 301,
                       "msg": "Invalid User name"
                       }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg": "You signed up"
        }
        return jsonify(retJson)


def verifyPw(username, password):
    if not UserExist(username):
        return False

    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens


class Detect(Resource):

    def post(self):

        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        if not UserExist(username):
            retJson = {
                "status": "301",
                "msg": "Invalid username"
            }
            return jsonify(retJson)
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status": "302",
                "msg": "Invalid password"
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)

        if num_tokens <= 0:
            retJson = {
                "status": 303,
                "msg": "OUT of TOKENS"
            }
            return jsonify(retJson)

        # Calculate edit distance
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)
        # Ratio between 0&1. if 1, txts are same
        ratio = text1.similarity(text2)

        retJson = {
            "status": 200,
            "similarity": ratio,
            "msg": "Similarity calculated"
        }

        current_tok = countTokens(username)
        users.update({
            "Username": username, },
            {
                "$set": {
                    "Tokens": current_tok - 1
                }
            })
        return jsonify(retJson)
