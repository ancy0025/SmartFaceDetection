# Save as test_opencv.py
import cv2
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    logging.error("Could not open webcam at index 0")
    exit(1)
logging.info("Webcam opened with index 0")

while True:
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to read frame")
        break
    cv2.imshow('Webcam Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
logging.info("Webcam test completed")