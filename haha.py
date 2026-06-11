import os
import json
import base64
import io
import requests
from datetime import datetime

import RPi.GPIO as GPIO
import time
import cv2
from ultralytics import YOLO

# === GPIO Pins ===
MOISTURE_PIN = 23   # Soil moisture sensor (digital D0 output)
LED_PIN = 17        # LED light
SPEAKER_PIN = 27    # Speaker/buzzer

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(SPEAKER_PIN, GPIO.OUT)

# === YOLO Bird Detection Model ===
model = YOLO("bird_model.pt")  # replace with your trained YOLOv8 model

# === Camera Setup ===
cap = cv2.VideoCapture(0)  # Pi Camera or USB cam

# === Supabase / Database config (use environment variables, do NOT hardcode keys) ===
SUPABASE_URL = os.getenv("https://tycixfmaksnripcyxcwi.supabase.co/rest/v1/")           # e.g. https://xxxxx.supabase.co
SUPABASE_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5Y2l4Zm1ha3NucmlwY3l4Y3dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYxNzI5NTMsImV4cCI6MjA5MTc0ODk1M30.u1e6yG52Tip7vfYbR-08p6JXQsbhiA-QhmCQCrSrlYY")   # service_role or anon key (choose appropriate)
DEVICE_ID = os.getenv("DEVICE_ID", "raspi-soil-01")
TABLE_NAME = os.getenv("SUPABASE_TABLE", "soil_moisture")  # table to insert into

if not SUPABASE_URL or not SUPABASE_API_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_API_KEY not set. Database uploads disabled.")
    DB_ENABLED = False
else:
    DB_ENABLED = True
    ENDPOINT = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{TABLE_NAME}"
    HEADERS = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def trigger_alert():
    """Turn on LED + speaker when bird detected."""
    GPIO.output(LED_PIN, GPIO.HIGH)
    GPIO.output(SPEAKER_PIN, GPIO.HIGH)
    print("Bird detected! LED + Speaker ON")
    time.sleep(3)
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.output(SPEAKER_PIN, GPIO.LOW)

def check_soil_moisture():
    """Read soil moisture sensor (digital)."""
    if GPIO.input(MOISTURE_PIN) == GPIO.LOW:
        return "Wet"
    else:
        return "Dry"

try:
    print("AGRIGUARD system running...")
    while True:
        # Soil moisture monitoring
        moisture_status = check_soil_moisture()
        print(f"Soil moisture: {moisture_status}")
        if moisture_status == "Dry":
            print("Soil is dry! Consider irrigation.")

        # Bird detection
        ret, frame = cap.read()
        if ret:
            results = model(frame)
            bird_found = False
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls]
                    if label.lower() == "bird" and conf > 0.7:
                        bird_found = True
            if bird_found:
                trigger_alert()

        time.sleep(2)

except KeyboardInterrupt:
    cap.release()
    GPIO.cleanup()
    print("System stopped.")
