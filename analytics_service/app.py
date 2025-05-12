from flask import Flask, jsonify
from pymongo import MongoClient
from collections import defaultdict

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client.online_learning

enrollments_collection = db.enrollments
courses_collection = db.courses

@app.route('/stats/enrollments', methods=['GET'])
def enrollment_stats():
    pipeline = [
        {"$group": {"_id": "$course_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    stats = list(enrollments_collection.aggregate(pipeline))
    for stat in stats:
        stat["course_id"] = stat.pop("_id")
    return jsonify(stats)

@app.route('/stats/popular_courses', methods=['GET'])
def popular_courses():
    pipeline = [
        {"$group": {"_id": "$course_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    popular = list(enrollments_collection.aggregate(pipeline))
    course_titles = {}
    
    # Fetch course titles from DB
    for item in popular:
        course_id = item['_id']
        course = courses_collection.find_one({"course_id": course_id})
        course_titles[course_id] = course['title'] if course else "Unknown"

    # Format result
    result = [
        {
            "course_id": item['_id'],
            "course_title": course_titles[item['_id']],
            "enrollments": item['count']
        }
        for item in popular
    ]
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
