"""
Simulated IoT Device
---------------------
Mimics a real sensor node (e.g., DHT11/DHT22 on an ESP32/Raspberry Pi)
pushing temperature & humidity readings to the cloud server every few
seconds. Run this alongside app.py to generate live data for the demo.
"""

import requests
import random
import time

SERVER_URL = "http://127.0.0.1:5000/api/data"
DEVICE_ID = "sensor-01"

def read_temperature():
    return round(random.uniform(20, 40), 2)   # simulate 20-40 C, occasionally crosses alert threshold

def read_humidity():
    return round(random.uniform(30, 90), 2)   # simulate 30-90 %

if __name__ == "__main__":
    print(f"[{DEVICE_ID}] Starting simulated sensor... sending data every 3s. Ctrl+C to stop.")
    while True:
        payload = {
            "device_id": DEVICE_ID,
            "temperature": read_temperature(),
            "humidity": read_humidity(),
        }
        try:
            r = requests.post(SERVER_URL, json=payload, timeout=5)
            print(f"Sent: {payload}  ->  Response: {r.status_code}")
        except requests.exceptions.RequestException as e:
            print("Error sending data:", e)
        time.sleep(3)