from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

# ✅ MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://qoisfirosi:testkntl@cluster0.hmf4k.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["iot"]
collection = db["sensor_data"]

@app.route("/push", methods=["POST"])
def receive_data():
    try:
        data = request.json
        if "sensor_id" not in data or "temperature" not in data or "humidity" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        # ✅ Use timezone-aware UTC time
        data["timestamp"] = datetime.now(timezone.utc)

        collection.insert_one(data)

        print("📥 Data received & saved:", data)
        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
