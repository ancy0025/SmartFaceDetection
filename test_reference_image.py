# Save as test_reference_image.py
import face_recognition
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_image(image_path):
    if not os.path.exists(image_path):
        logging.error(f"Image not found: {image_path}")
        return
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            logging.info(f"Found {len(encodings)} face(s) in {image_path}")
        else:
            logging.warning(f"No faces detected in {image_path}")
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    image_path = "images/anurag.jpg"
    test_image(image_path)