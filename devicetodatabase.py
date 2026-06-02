import RPi.GPIO as GPIO
import time
import requests
import json
from datetime import datetime

# Supabase details
SUPABASE_URL = "https://tycixfmaksnripcyxcwi.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5Y2l4Zm1ha3NucmlwY3l4Y3dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYxNzI5NTMsImV4cCI6MjA5MTc0ODk1M30.u1e6yG52Tip7vfYbR-08p6JXQsbhiA-QhmCQCrSrlYY"
endpoint = f"{SUPABASE_URL}/rest/v1/soil_moisture"

# Example soil moisture data
payload = {
    "device_id": "raspi-soil-01",
    "moisture_level": 42.5,
    "ts": datetime.utcnow().isoformat()
}

# Headers required by Supabase
headers = {
    "apikey": SUPABASE_API_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# GPIO setup
SENSOR_PIN = 4   # connect D0 pin of sensor to GPIO4
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

def read_soil_moisture():
    # Digital read: 0 = wet, 1 = dry
    value = GPIO.input(SENSOR_PIN)
    if value == 0:
        moisture_percent = 80   # approximate wet
    else:
        moisture_percent = 20   # approximate dry
    return moisture_percent

try:
    while True:
        moisture = read_soil_moisture()
        payload = {
            "device_id": "raspi-soil-01",
            "moisture_level": moisture,
            "ts": datetime.utcnow().isoformat()
        }
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        print(f"Soil Moisture: {moisture}% | Status: {response.status_code}")
        time.sleep(10)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Stopped.")
