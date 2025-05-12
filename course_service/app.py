from flask import Flask, request, jsonify
from pymongo import MongoClient
from flasgger import Swagger

app = Flask(__name__)
# swagger_config = {
#     "headers": [],
#     "specs": [
#         {
#             "endpoint": 'apispec_1',
#             "route": '/apispec_1.json',
#             "rule_filter": lambda rule: True,  # all routes
#             "model_filter": lambda tag: True,  # all models
#         }
#     ],
#     "static_url_path": "/flasgger_static",
#     "swagger_ui": True,
#     "specs_route": "/apidocs/"
# }

# Swagger(app, config=swagger_config)


client = MongoClient("mongodb://mongo:27017/")
db = client.online_learning
courses_collection = db.courses


@app.route('/')
def welcome():
    return "Course Service is running"

@app.route('/courses', methods=['POST'])
def add_course():
    data = request.json
    existing_course = courses_collection.find_one({"course_id": data.get("course_id")})
    
    if existing_course:
        return jsonify({"error": "Course with this course_id already exists"}), 400

    courses_collection.insert_one(data)
    return jsonify({"message": "Course added"})
# def add_course():
#     data = request.json
#     courses_collection.insert_one(data)
#     return jsonify({"message": "Course added"})

@app.route('/courses', methods=['GET'])
def list_courses():
    courses = list(courses_collection.find({}, {'_id': 0}))
    return jsonify(courses)

@app.route('/course/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = courses_collection.find_one({"course_id": course_id}, {"_id": 0})
    if course:
        return jsonify(course)
    else:
        return jsonify({"error": "Course not found"}), 404
    
@app.route('/course/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.json
    result = courses_collection.update_one({"course_id": course_id}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Course updated"})
    else:
        return jsonify({"error": "Course not found"}), 404

@app.route('/course/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    result = courses_collection.delete_one({"course_id": course_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Course deleted"})
    else:
        return jsonify({"error": "Course not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)