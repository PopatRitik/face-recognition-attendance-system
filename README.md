# Face Recognition Attendance System

## Description:
This project is a Flask-based system for real-time face detection, recognition, and attendance logging using OpenCV and face_recognition library. It integrates with MySQL for face data storage and Telegram API for attendance notifications.
![image](https://github.com/user-attachments/assets/e6c6ba79-1e77-42e8-97aa-5dfee9f887a7)



## Technologies Used:
- Python
- Flask
- MySQL
- OpenCV
- face_recognition
- Telegram API

## Features:
- Real-time face detection and recognition
- Recognition classifies into 3 types: Unknown, Marked and Unmarked 
- Attendance logging with timestamp and match percentage
- Telegram notifications for attendance updates

## Project Flow:
![image](https://github.com/user-attachments/assets/e81680bf-88b9-40f1-b57e-a196c146cf97)


## Setup Instructions:
1. Install Python and MySQL server.
2. Clone the repository.
3. Install dependencies: `pip install -r requirements.txt`.
4. Set up MySQL database and update `db_config` in `app.py`.
5. Run the application: `python app.py`.

## Folder Structure:
- `/faces`: Directory to store captured face images.
- `/attendance_logs`: Directory to store attendance CSV logs.

## Contributors:
![Dev Parmar](https://github.com/Spy-boy-07.png?size=60) **[Dev Parmar](https://github.com/Spy-boy-07)** - *Project Creator* <br>
![Ritik Popat](https://github.com/PopatRitik.png?size=60) **[Ritik Popat](https://github.com/PopatRitik)** - *Database Handling* <br>
<img src="https://github.com/hetparmar30.png?size=100" width="50" height="50"> **[Het Parmar](https://github.com/hetparmar30)**  
<img src="https://github.com/jennybhut14.png?size=100" width="50" height="50">  **[Jenny Bhut](https://github.com/jennybhut14)** 
<img src="https://github.com/ayusagarwal?size=100" width="50" height="50">  **[Jenny Bhut](https://github.com/ayusagarwal)** 

