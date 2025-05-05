import cv2
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_camera(index):
    logging.info(f"Testing webcam index {index}")
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        logging.error(f"Could not open webcam at index {index}")
        return False
    camera_name = cap.getBackendName()
    logging.info(f"Webcam at index {index} using backend: {camera_name}")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logging.error(f"Failed to read frame at index {index}")
            break
        cv2.imshow(f'Webcam Test - Index {index}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return True

for index in [0, 1, 2, 3, -1]:
    if test_camera(index):
        logging.info(f"Webcam found at index {index}")
    else:
        logging.warning(f"No webcam at index {index}")