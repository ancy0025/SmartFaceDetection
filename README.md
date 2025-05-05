# SmartFaceDetection

SmartFaceDetection is an advanced facial recognition-based attendance system designed to simplify the attendance process using real-time face recognition technology. The system captures live images from a webcam, processes them to recognize faces, and logs attendance based on the identified faces. Built with deep learning algorithms and computer vision technologies such as OpenCV and dlib, this project is highly accurate and efficient in detecting and recognizing faces.

## Table of Contents

- [Project Overview](#project-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Overview

The SmartFaceDetection system leverages deep learning and computer vision to automate the attendance process in environments like classrooms, offices, and events. Key features include real-time face recognition, automated attendance logging, and accurate identification of individuals even in dynamic environments.

### Key Benefits:
- **Automated Attendance**: No manual check-in required, reducing human error.
- **Real-Time Recognition**: The system works in real-time, immediately identifying faces as they appear.
- **Scalable**: Suitable for classrooms, offices, and events with multiple attendees.
- **Enhanced Security**: Facial recognition improves security by verifying the identity of users.

## Installation

Follow these steps to install and run the SmartFaceDetection system locally:

### Requirements

- Python 3.x
- OpenCV
- TensorFlow or Keras (for deep learning models)
- dlib (for facial landmark detection)
- Numpy
- Other dependencies listed in `requirements.txt`

### Steps

1. **Clone the repository:**
    ```bash
    git clone https://github.com/ancy0025/SmartFaceDetection.git
    ```

2. **Install dependencies:**
    You can install all the required libraries by running:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment:**
    - Ensure you have a webcam connected and functional for real-time face detection.
    - You may need to download pre-trained models (like face recognition models) if not included in the repository.
    
4. **Optional: Set up a virtual environment**:
    It is recommended to use a virtual environment to manage dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate  # For Windows
    ```

## Usage

To use the system for face recognition and attendance logging:

1. **Run the main script:**
    ```bash
    python app.py
    ```

2. **Webcam Activation:**
    - The application will activate the webcam, and it will start capturing live video for face recognition.
    - Each detected face will be compared with pre-stored face data and marked as "present" if recognized.

3. **Attendance Logging:**
    - The attendance will be automatically logged and saved in a CSV file with timestamps and recognized names.
    - The log will be stored in a folder specified in the `config.py` or similar configuration file.

4. **Face Database Management:**
    - Before starting the recognition, you need to register faces in the system. This can be done by running a face registration script where you capture a face image and assign it to a person’s ID.

5. **View Attendance:**
    - Check the attendance logs saved in the `attendance.csv` file or access the logs through a graphical interface if available.

## Features

- **Real-Time Face Recognition**: Detects faces using a webcam and processes them instantly.
- **Attendance Tracking**: Logs attendance based on recognized faces, including timestamps and individual IDs.
- **Multiple Face Support**: Recognizes multiple people at once.
- **Dynamic Face Recognition**: Can recognize faces in varying light conditions, angles, and environments.
- **CSV Attendance Log**: Automatically records attendance in a CSV file for easy access and record keeping.
- **User-Friendly Interface**: Simple to use with minimal setup and easy to understand outputs.

## Technologies Used

The SmartFaceDetection system is built using the following technologies:

- **Python**: The core programming language used for the project.
- **OpenCV**: A powerful library for image processing and computer vision tasks, used for face detection.
- **dlib**: A toolkit for machine learning and data analysis, used for facial landmark detection and recognition.
- **TensorFlow/Keras**: For building and utilizing pre-trained deep learning models for face recognition.
- **Numpy**: Used for numerical computations and array handling.

## License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [dlib](http://dlib.net/): For facial landmark detection.
- [OpenCV](https://opencv.org/): For computer vision tasks.
- [TensorFlow](https://www.tensorflow.org/): For deep learning-based recognition.
- Contributors and other open-source projects that made this project possible.
