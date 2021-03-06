import bcrypt
import spacy
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import en_core_web_sm
import os

app = Flask(__name__)
api = Api(app)

#client = MongoClient(os.environ.get('MONGODB_HOST', 'localhost'))
client = MongoClient("mongodb://db:27017")

db = client.SimilarityDB
users = db["Users"]


def UserExist(username):
    if db.users.count_documents({"Username": username}) == 0:
        return False
    else:
        return True


class Register(Resource):

    def post(self):
        postedData = request.get_json()

        username = postedData["Username"]
        password = postedData["Password"]

        if UserExist(username):
            retJson = {"status": 301,
                       "msg": "Invalid User name"
                       }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        db.users.insert_one({
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

    hashed_pw = db.users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    tokens = db.users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens


class Detect(Resource):

    def post(self):

        postedData = request.get_json()

        username = postedData["Username"]
        password = postedData["Password"]
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
        #nlp = spacy.load("en_core_web_sm")
        nlp = en_core_web_sm.load()

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
        db.users.update_one({
            "Username": username, },
            {
                "$set": {
                    "Tokens": current_tok - 1
                }
            })
        return jsonify(retJson)


class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["Username"]
        password = postedData["admin_pw"]
        refill_ammount = postedData["refill"]

        if not UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid username"
            }
            return jsonify(retJson)

        correct_pw = "abc123"
        if not password == correct_pw:
            retJson = {
                "status": "302",
                "msg": "Invalid admin password"
            }
            return jsonify(retJson)

        # current_tokens = countTokens(username)
        db.users.update_one({
            "Username": username
        }, {
            "$set": {
                "Tokens": refill_ammount
            }
        })
        retJson = {
            "status": 301,
            "msg": "REFILLED TOKENS"
        }
        return jsonify(retJson)


api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0', port=5000)
