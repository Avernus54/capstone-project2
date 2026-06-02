import RPi.GPIO as GPIO
import time
import cv2
from ultralytics import YOLO

# GPIO setup
LED_PIN = 17
BUZZER_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Load YOLOv8 bird detection model
model = YOLO("bird_detection.pt")  # your trained model file

# Open camera (0 = default USB cam, use 0 or 1 depending on setup)
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Run inference
        results = model(frame)

        # Check detections
        bird_found = False
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])        # class index
                conf = float(box.conf[0])    # confidence
                label = model.names[cls]     # class name

                if label.lower() == "bird" and conf > 0.8:
                    bird_found = True

        # Trigger GPIO
        if bird_found:
            GPIO.output(LED_PIN, GPIO.HIGH)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            print("Bird detected! LED + Buzzer ON")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            GPIO.output(BUZZER_PIN, GPIO.LOW)

        time.sleep(1)

except KeyboardInterrupt:
    cap.release()
    GPIO.cleanup()
    print("Stopped.")
