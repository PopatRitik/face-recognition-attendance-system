from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import cv2
import face_recognition as fr
import numpy as np
import os
import datetime
import csv
import requests

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mynameispopat12345!@#$%',
    'database': 'face_recognition_db'
}

# Initialize variables for face recognition and attendance tracking
known_names = []
known_name_encodings = []
attendance_log = []
id_frequency_map = {}  # Map to store the frequency of each detected ID
suspected_ids = set()  # Set to store IDs with a frequency of 7

# Folder to save captured faces and attendance
faces_folder = "faces"
attendance_folder = "attendance_logs"


def add_face_to_database(face_id, name, chat_id, image_name):
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert face data into the faces table
        query = "INSERT INTO faces (id, name, chat_id, user_id) VALUES (%s, %s, %s, %s)"
        values = (face_id, name, chat_id, image_name)
        cursor.execute(query, values)

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error adding face to the database: {e}")


def write_attendance_log(date_str, log_entries):
    csv_file_path = os.path.join(
        attendance_folder, f"attendance_{date_str}.csv")

    # Check if the CSV file already exists
    file_exists = os.path.exists(csv_file_path)

    # Open the CSV file in append mode (a) if it exists, otherwise in write mode (w)
    with open(csv_file_path, 'a' if file_exists else 'w', newline='') as csvfile:
        fieldnames = ["Name", "ID", "Timestamp", "MatchPercent"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the file doesn't exist, write the header
        if not file_exists:
            writer.writeheader()

        # Write the log entries
        for entry in log_entries:
            writer.writerow(entry)

    id_frequency_map.clear()


telegram_bot_token = '6728316261:AAHRd_lopYRyqKtVWvyW-ACtgnj1ptB1UO0'

# Telegram API URL for sending messages
telegram_api_url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'


def send_telegram_message(chat_id, message):
    """
    Function to send a message to the Telegram Bot API.
    """
    print(message)
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(telegram_api_url, params=params)
    return response.json()


def is_id_in_csv(date_str, user_id):
    suspected_ids = set()
    csv_file_path = os.path.join(
        attendance_folder, f"attendance_{date_str}.csv")
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'ID' in row:
                    suspected_ids.add(row['ID'])
    if user_id in suspected_ids:
        return 1
    else:
        return 0

# Load known faces from the "faces" folder


def load_known_faces():
    known_names.clear()
    known_name_encodings.clear()

    for filename in os.listdir(faces_folder):
        if filename.endswith(".jpg"):
            image_path = os.path.join(faces_folder, filename)
            name, _ = os.path.splitext(filename)
            known_names.append(name)

            image = fr.load_image_file(image_path)
            encoding = fr.face_encodings(image)[0]
            known_name_encodings.append(encoding)


date_str = datetime.datetime.now().strftime("%d-%m-%Y")
time_str = datetime.datetime.now().strftime("%H:%M")


def get_chat_id_by_user_id(user_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # cursor.execute("SELECT chat_id FROM faces WHERE user_id = ?", (user_id,))

    print(user_id)
    query1 = "SELECT chat_id FROM faces WHERE user_id=%s"
    values1 = (user_id,)
    cursor.execute(query1, values1)

    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None


def get_face_id_by_user_id(user_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # cursor.execute("SELECT chat_id FROM faces WHERE user_id = ?", (user_id,))

    print(user_id)
    query1 = "SELECT id FROM faces WHERE user_id=%s"
    values1 = (user_id,)
    cursor.execute(query1, values1)

    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None


def get_name_by_user_id(user_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # cursor.execute("SELECT chat_id FROM faces WHERE user_id = ?", (user_id,))

    print(user_id)
    query1 = "SELECT name FROM faces WHERE user_id=%s"
    values1 = (user_id,)
    cursor.execute(query1, values1)

    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None

# Function to capture a frame from the webcam and perform face detection


def detect_faces(chat_id):
    video_capture = cv2.VideoCapture(0)

    # Load known faces from the "faces" folder
    load_known_faces()

    while True:
        # Clear attendance log at the beginning of each iteration
        attendance_log = []

        ret, frame = video_capture.read()

        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations in the current frame
        face_locations = fr.face_locations(rgb_frame, model="hog")
        face_encodings = fr.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = fr.compare_faces(known_name_encodings, face_encoding)
            name = "Unknown"
            face_distance_percent = None  # Set face_distance_percent to None for unknown faces

            if any(matches):
                face_distances = fr.face_distance(
                    known_name_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                face_distance_percent = (
                    1 - face_distances[best_match_index]) * 100
                name = known_names[best_match_index]

                # Update frequency map for the detected ID
                user_id = name.split('_')[1]
                id_frequency_map[user_id] = id_frequency_map.get(
                    user_id, 0) + 1
                # Check if the frequency for a particular ID hits 7
                if id_frequency_map.get(user_id, 0) == 7:
                    if is_id_in_csv(date_str, user_id) == 1:
                        pass
                    else:
                        # Write attendance log entry to CSV file
                        log_entry = {"Name": name, "ID": user_id, "Timestamp": datetime.datetime.now(
                        ).strftime("%Y-%m-%d %H:%M:%S"), "MatchPercent": face_distance_percent}
                        attendance_log.append(log_entry)
                        write_attendance_log(date_str, [log_entry])
                        # Reset the frequency for this ID in the map
                        chat_id = get_chat_id_by_user_id(name)
                        name1 = get_name_by_user_id(name)
                        face_id1 = get_face_id_by_user_id(name)
                        # Corrected line
                        message = ("Hello " + name1 + "("+face_id1 + "), Your 📅 attendance has been marked for date : " 
                                  + date_str + " at time:"+time_str+". Good Day Ahead!👍")

                        send_telegram_message(chat_id, message)
                        id_frequency_map[user_id] = 0

                # Check if the ID is in the CSV file for the current date
                if is_id_in_csv(date_str, user_id):
                    cv2.rectangle(frame, (left, top),
                                  (right, bottom), (0, 255, 0), 2)
                    cv2.rectangle(frame, (left, bottom - 15),
                                  (right, bottom), (0, 255, 0), cv2.FILLED)
                else:
                    cv2.rectangle(frame, (left, top),
                                  (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 15),
                                  (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, f"{name} ({face_distance_percent:.2f}%)",
                            (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
                # For unknown faces, you can choose to perform any specific action
                # For example, you might want to mark them differently in the display
                cv2.rectangle(frame, (left, top),
                              (right, bottom), (128, 128, 128), 2)
                cv2.rectangle(frame, (left, bottom - 15),
                              (right, bottom), (128, 128, 128), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, "Unknown", (left + 6, bottom - 6),
                            font, 1.0, (255, 255, 255), 1)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close all windows
    video_capture.release()
    cv2.destroyAllWindows()


# Route for home page with real-time data
@app.route('/')
def home():
    # Read CSV file data
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    csv_file_path = os.path.join(
        attendance_folder, f"attendance_{date_str}.csv")

    data = []
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = [row for row in reader]

    # Render the template with real-time data
    return render_template('index.html', data=data)

# Route to add faces for training


@app.route('/add_face', methods=['POST'])
def add_face():
    global known_names, known_name_encodings

    # Get name, ID, and chat_id from the form
    name = request.form['name']
    face_id = request.form['id']
    chat_id = request.form['chat_id']

    # Capture a frame from the webcam
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()

    # Save the captured face image
    image_name = f"{name}_{face_id}.jpg"
    image_name1 = f"{name}_{face_id}"
    image_path = os.path.join(faces_folder, image_name)
    cv2.imwrite(image_path, frame)

    # Add face data to the MySQL database
    add_face_to_database(face_id, name, chat_id, image_name1)

    # Load known faces from the "faces" folder
    load_known_faces()

    # Release the webcam
    video_capture.release()

    return redirect(url_for('home'))


# Route to start face detection
@app.route('/detect_faces', methods=['GET', 'POST'])
def detect_faces_route():
    # Get chat_id from the form (you may use a form submission or any other mechanism)
    chat_id = request.form.get('chat_id')

    # Call detect_faces function with the provided chat_id
    detect_faces(chat_id)

    # Save attendance log to a CSV file with the current date
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    write_attendance_log(date_str, attendance_log)

    return redirect(url_for('home'))


if __name__ == '__main__':
    # Create the "faces" folder and "attendance_logs" folder if they don't exist
    if not os.path.exists(faces_folder):
        os.makedirs(faces_folder)
    if not os.path.exists(attendance_folder):
        os.makedirs(attendance_folder)

    app.run(debug=True)
