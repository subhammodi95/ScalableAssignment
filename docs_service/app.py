from flask import Flask, request, jsonify
from pymongo import MongoClient
from flasgger import Swagger

app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017/")
db = client.online_learning
users_collection = db.users
courses_collection = db.courses

# Swagger config
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # include all routes
            "model_filter": lambda tag: True,  # include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, config=swagger_config)

@app.route('/')
def welcome():
    return "Docs Service is running"

@app.route('/courses', methods=['GET'])
def list_courses():
    courses = list(courses_collection.find({}, {'_id': 0}))
    return jsonify(courses)

@app.route('/users', methods=['GET'])
def get_all_users():
    users = users_collection.find({}, {"_id": 0})
    return jsonify(list(users))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
