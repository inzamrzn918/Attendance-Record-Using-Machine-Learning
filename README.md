# Attendance Record Using Machine Learning

This project presents an advanced system designed to automate attendance tracking and monitor student emotions through cutting-edge machine-learning techniques. By integrating facial recognition and emotion detection, the system provides real-time insights into student presence and emotional well-being, enhancing the educational experience.

## Features

- **Facial Recognition**: Accurately identifies and verifies student identities to streamline attendance processes.
- **Emotion Detection**: Analyzes facial expressions to assess and record students' emotional states during sessions.
- **User-Friendly Web Interface**: Offers an intuitive and responsive web-based platform for administrators and users.
- **Secure Database Management**: MySQL is employed to efficiently store and retrieve user data, attendance logs, and emotional assessments.

## Installation

To deploy this system, follow the steps below:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/inzamrzn918/Attendance-Record-Using-Machine-Learning.git
   cd Attendance-Record-Using-Machine-Learning
   ```

2. **Install Dependencies**:

   Ensure Python is installed on your system. Install the required packages using:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database**:

   - **Access MySQL**:

     ```bash
     mysql -u root -p
     ```

   - **Create the Database**:

     ```sql
     CREATE DATABASE mcaprj;
     ```

   - **Configure Database Settings**:

     Update the database credentials in `main.py` if your MySQL username or password differs from the default (`username: "root"`, `password: ""`).

   - **Initialize the Database**:

     ```python
     from main import db
     db.create_all()
     ```

4. **Launch the Application**:

   Start the Flask server:

   ```bash
   python main.py
   ```

   The application will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Project Structure

- `app.py`: Sets up the Flask application and defines routes.
- `camera.py`: Manages webcam operations, including image capture and processing.
- `main.py`: Handles database configurations and application initialization.
- `mose_control.py`: Implements mouse control features based on facial gestures.
- `save.py`: Contains functions for saving captured images and related data.
- `requirements.txt`: Lists all necessary Python dependencies for the project.
- `templates/`: Houses HTML templates for the web interface.
- `static/`: Contains static assets such as CSS, JavaScript, and images.
- `models/`: Includes machine learning models for facial and emotion recognition.
- `images/`: Directory designated for storing captured images.
- `flask_session/`: Stores session data for user interactions.

## Usage

1. **Registering New Students**:

   - Navigate to the "Add Student" section via the web interface.
   - Input the student's details and capture their image to enroll them into the system.

2. **Recording Attendance**:

   - Access the "Mark Attendance" section.
   - The system will activate the webcam to detect and recognize student faces, logging attendance along with their current emotional states.

3. **Reviewing Attendance Logs**:

   - Visit the "Attendance Records" section to view, search, and manage attendance data.

## Technical Specifications

- **Programming Language**: Python
- **Web Framework**: Flask
- **Machine Learning Libraries**: OpenCV, TensorFlow/Keras
- **Database**: MySQL

## Contribution Guidelines

Contributions to enhance this project are welcome. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Implement your changes and commit them with descriptive messages.
4. Push your branch to your forked repository.
5. Submit a pull request detailing your changes and their benefits.

## License

This project is licensed under the MIT License. The LICENSE file in the repository provides more information.

---
