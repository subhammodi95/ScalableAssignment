from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client.online_learning
feedback_collection = db.feedbacks

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()

    # Basic validation
    required_fields = ["username", "course_id", "rating", "comment"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    feedback = {
        "username": data["username"],
        "course_id": data["course_id"],
        "rating": data["rating"],
        "comment": data["comment"],
        "submitted_at": str(datetime.datetime.now())
    }

    feedback_collection.insert_one(feedback)
    return jsonify({"message": "Feedback submitted successfully"}), 201

@app.route('/feedback/<course_id>', methods=['GET'])
def get_feedback(course_id):
    feedbacks = list(feedback_collection.find({"course_id": course_id}, {"_id": 0}))
    return jsonify(feedbacks), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
