"""
Cloud-Based IoT Monitoring System - Backend Server
----------------------------------------------------
Acts as the "cloud" component: receives data pushed by IoT devices
(real or simulated), stores it in a database, and serves a live
dashboard + REST API. Deployable to any cloud host (AWS EC2, Render,
Heroku, PythonAnywhere, etc.) exactly as-is.
"""

from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(__file__), "sensor_data.db")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def dashboard():
    return render_template("index.html")


# ---- Device -> Cloud: ingest sensor reading ----
@app.route("/api/data", methods=["POST"])
def receive_data():
    payload = request.get_json(force=True)
    device_id = payload.get("device_id", "unknown")
    temperature = payload.get("temperature")
    humidity = payload.get("humidity")
    timestamp = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO readings (device_id, temperature, humidity, timestamp) VALUES (?, ?, ?, ?)",
        (device_id, temperature, humidity, timestamp),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "stored_at": timestamp}), 201


# ---- Dashboard -> Cloud: fetch recent readings ----
@app.route("/api/data", methods=["GET"])
def get_data():
    limit = int(request.args.get("limit", 30))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT device_id, temperature, humidity, timestamp FROM readings "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = c.fetchall()
    conn.close()

    rows.reverse()  # oldest -> newest for charting
    data = [
        {"device_id": r[0], "temperature": r[1], "humidity": r[2], "timestamp": r[3]}
        for r in rows
    ]
    return jsonify(data)


# ---- Simple threshold-based alert check ----
@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    TEMP_THRESHOLD = 35.0
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT device_id, temperature, timestamp FROM readings "
        "WHERE temperature > ? ORDER BY id DESC LIMIT 10",
        (TEMP_THRESHOLD,),
    )
    rows = c.fetchall()
    conn.close()
    alerts = [{"device_id": r[0], "temperature": r[1], "timestamp": r[2]} for r in rows]
    return jsonify(alerts)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)