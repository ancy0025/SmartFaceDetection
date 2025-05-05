# Save as test_opencv_enhanced.py
import cv2
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_webcam(index, backend, backend_name):
    logging.info(f"Testing webcam at index {index} with backend {backend_name}")
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        logging.error(f"Could not open webcam at index {index} with {backend_name}")
        return False
    
    # Add delay to stabilize camera
    time.sleep(2)
    logging.info(f"Webcam opened at index {index} with {backend_name}")

    retries = 3
    for attempt in range(retries):
        ret, frame = cap.read()
        if not ret:
            logging.warning(f"Failed to read frame at index {index} with {backend_name}, attempt {attempt + 1}/{retries}")
            time.sleep(1)
            continue
        logging.info(f"Successfully read frame at index {index} with {backend_name}")
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error(f"Frame read failed during display at index {index}")
                break
            cv2.imshow(f'Webcam Test - Index {index} ({backend_name})', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        logging.info(f"Webcam test completed for index {index} with {backend_name}")
        return True
    
    logging.error(f"Failed to read frames after {retries} attempts at index {index} with {backend_name}")
    cap.release()
    return False

# Test multiple indices and backends
backends = [
    (cv2.CAP_AVFOUNDATION, "CAP_AVFOUNDATION"),
    (cv2.CAP_ANY, "CAP_ANY"),
    (cv2.CAP_V4L2, "CAP_V4L2")
]
indices = [0, 1, 2, -1]

for index in indices:
    for backend, backend_name in backends:
        if test_webcam(index, backend, backend_name):
            logging.info(f"Success: Webcam works at index {index} with {backend_name}")
        else:
            logging.warning(f"Failure: Webcam does not work at index {index} with {backend_name}")