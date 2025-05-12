from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Create a retry-enabled session
def get_retry_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,  # wait 1s, then 2s, then 4s
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session

session = get_retry_session()

app = Flask(__name__)
client = MongoClient("mongodb://mongo:27017/")
db = client.online_learning
enrollments_collection = db.enrollments

@app.route('/enroll', methods=['POST'])
def enroll():
    data = request.json
    username = data.get('username')
    course_id = data.get('course_id')

    # user_response = requests.get(f'http://user-service:5001/get_user/{username}')
    user_response = session.get(f'http://user-service:5001/get_user/{username}')

    if user_response.status_code != 200:
        return jsonify({"message": "User does not exist"}), 404

    enrollment = {
        "username": username,
        "course_id": course_id
    }
    enrollments_collection.insert_one(enrollment)
    return jsonify({"message": "Enrolled successfully"})

@app.route('/my-courses/<username>', methods=['GET'])
def get_user_courses(username):
    enrolled = list(enrollments_collection.find({"username": username}, {"_id": 0}))
    enriched_courses = []

    for record in enrolled:
        course_id = record['course_id']
        try:
            # Talk to course_service to get course details
            # response = requests.get(f'http://course-service:5002/course/{course_id}')
            response = session.get(f'http://course-service:5002/course/{course_id}')

            if response.status_code == 200:
                course_info = response.json()
                enriched_courses.append({
                    "username": username,
                    "course_id": course_id,
                    "course_title": course_info.get("title", "Unknown")
                })
            else:
                enriched_courses.append({
                    "username": username,
                    "course_id": course_id,
                    "course_title": "Not Found"
                })
        except requests.exceptions.RequestException:
            enriched_courses.append({
                "username": username,
                "course_id": course_id,
                "course_title": f"Error Fetching Title"
            })

    return jsonify(enriched_courses)

@app.route('/enroll', methods=['PUT'])
def update_enrollment():
    data = request.json
    username = data.get('username')
    old_course_id = data.get('old_course_id')
    new_course_id = data.get('new_course_id')

    result = enrollments_collection.update_one(
        {"username": username, "course_id": old_course_id},
        {"$set": {"course_id": new_course_id}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Enrollment not found"}), 404

    return jsonify({"message": "Enrollment updated"})

@app.route('/enroll', methods=['DELETE'])
def delete_enrollment():
    data = request.json
    username = data.get('username')
    course_id = data.get('course_id')

    result = enrollments_collection.delete_one({"username": username, "course_id": course_id})

    if result.deleted_count == 0:
        return jsonify({"error": "Enrollment not found"}), 404

    return jsonify({"message": "Enrollment deleted"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)