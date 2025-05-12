from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# Connect to MongoDB (mongo is the service name in docker-compose)
client = MongoClient("mongodb://mongo:27017/")
db = client.online_learning
certificates_collection = db.certificates

@app.route('/generate', methods=['POST'])
def generate_certificate():
    data = request.get_json()

    # Check if certificate already exists
    existing = certificates_collection.find_one({
        "user_id": data["user_id"],
        "course_id": data["course_id"]
    })

    if existing:
        return jsonify({"message": "Certificate already exists", "certificate": existing}), 200

    cert = {
        "user_id": data["user_id"],
        "course_id": data["course_id"],
        "issued_on": str(datetime.datetime.now()),
        "certificate": f"Certificate for {data['user_id']} in course {data['course_id']}"
    }

    certificates_collection.insert_one(cert)
    return jsonify(cert), 201

@app.route('/certificate/<user_id>/<course_id>', methods=['GET'])
def get_certificate(user_id, course_id):
    cert = certificates_collection.find_one({
        "user_id": user_id,
        "course_id": course_id
    })

    if not cert:
        return jsonify({"message": "Certificate not found"}), 404

    cert['_id'] = str(cert['_id'])  # Convert ObjectId to string
    return jsonify(cert), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
