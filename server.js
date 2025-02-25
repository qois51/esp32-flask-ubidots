const express = require("express");
const { MongoClient } = require("mongodb");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
const PORT = 3000;

// **MongoDB Connection**
const MONGO_URI = "mongodb+srv://qoisfirosi:testkntl@cluster0.hmf4k.mongodb.net/?appName=Cluster0";
const DB_NAME = "iot"; // Database Name
const COLLECTION_NAME = "sensor_data"; // Collection Name

let db;

// **Connect to MongoDB**
async function connectDB() {
    try {
        const client = new MongoClient(MONGO_URI);
        await client.connect();
        db = client.db(DB_NAME);
        console.log("✅ Connected to MongoDB");
    } catch (error) {
        console.error("❌ MongoDB Connection Error:", error);
    }
}

connectDB();

// **Middleware**
app.use(cors());
app.use(bodyParser.json());

// **Route to Receive ESP32 Data**
app.post("/push", async (req, res) => {
    try {
        const { sensor_id, temperature, humidity } = req.body;

        if (!sensor_id || temperature === undefined || humidity === undefined) {
            return res.status(400).json({ message: "Invalid data format" });
        }

        // **Insert into MongoDB**
        const result = await db.collection(COLLECTION_NAME).insertOne({
            sensor_id,
            temperature,
            humidity,
            timestamp: new Date(),
        });

        console.log("📥 Data received & saved:", req.body);
        res.status(200).json({ message: "Data saved successfully", id: result.insertedId });
    } catch (error) {
        console.error("❌ Error saving data:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// **Start Server**
app.listen(PORT, () => {
    console.log(`🚀 Server running at http://0.0.0.0:${PORT}`);
});
