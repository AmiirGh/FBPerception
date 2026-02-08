import socket
import json
import time
import struct
import threading
import traceback
from vibration import *
import csv
import pandas as pd
import os
import subprocess
import sys
import sounddevice as sd
from scipy.io.wavfile import write

def send_data_with_prefix(client_socket, data):
    """Send JSON data with a length prefix."""
    json_data = json.dumps(data)
    json_data_bytes = json_data.encode('utf-8')
    length_prefix = struct.pack('!I', len(json_data_bytes))
    client_socket.sendall(length_prefix)
    client_socket.sendall(json_data_bytes)


def receive_data_with_prefix(client_socket):
    """Receive JSON data with a length prefix."""
    length_data = client_socket.recv(4)
    if len(length_data) < 4:
        return None

    message_length = struct.unpack('!I', length_data)[0]
    json_data = b""
    while len(json_data) < message_length:
        chunk = client_socket.recv(message_length - len(json_data))
        if not chunk:
            return None
        json_data += chunk

    try:
        return json.loads(json_data.decode())
    except json.JSONDecodeError:
        return None


class SimpleClient:
    def __init__(self, host="127.0.0.1", port=12345):
        self.client_socket = None
        self.running = True
        self.connect_to_server(host, port)
        self.vib = VibrationClient()
        self.invalid_degree_int = 10
        self.invalid_level = 10
        self.subject_name = "temp"
        self.subject_id = 0
        self.experiment_phase = 0
        self.old_experiment_phase = 0
        self.part_number = 0 # there are 3 parts all the same
        self.prev_timestamp = 1
        self.isFirstTimeRecording = True
    def read_subject_info(self):
        df = pd.read_excel('subject_info.xlsx')
        self.subject_name = df.loc[df['Subject_Info'] == 'name', 'Value'].values[0]
        self.subject_id = df.loc[df['Subject_Info'] == 'ID', 'Value'].values[0]
        print(self.subject_name, self.subject_id)


    def connect_to_server(self, host, port):
        """Connect to the server with retry logic."""
        while True:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((host, port))
                print("Connected to the server successfully!")
                break
            except (socket.error, ConnectionRefusedError):
                print("Server unavailable. Retrying in 0.2 seconds...")
                time.sleep(0.2)

    def receive_data(self):
        """Receive data from server in a separate thread and log values to file."""

        log_file = "received_data_" + str(self.subject_name) + "_" + str(self.subject_id) + ".csv"
        file_exists = os.path.isfile(log_file)

        try:
            with open(log_file, mode="a", newline="") as f:
                writer = csv.writer(f)

                if not file_exists:
                    writer.writerow([
                        "timestamp",
                        "interval_number",
                        "trial_number",
                        "is_dynamic_obstacle_present",
                        "degree",
                        "level",
                        "feedback_modality",
                        "right_index_button",
                        "left_index_button",
                        "right_thumbstick_x",
                        "right_thumbstick_y",
                        "number_of_collision",
                        "head_position",
                        "head_rotation",
                        # "head_pos_x",
                        # "head_pos_y",
                        # "head_pos_z",
                        # "head_rot_x",
                        # "head_rot_y",
                        # "head_rot_z",
                        "collision_position",
                    ])

                while self.running:
                    try:
                        data = receive_data_with_prefix(self.client_socket)

                        if not data:
                            continue
                        timestamp = data.get("timestamp")
                        interval_number = data.get("intervalNumber")
                        trial_number = data.get("trialNumber")
                        is_dynamic_obstacle_present = data.get("isDynamicObstaclePresent")

                        degree = data.get("degree")
                        level = data.get("level")
                        feedback_modality = data.get("feedbackModality")

                        right_index_button = data.get("rightIndexButton")
                        left_index_button = data.get("leftIndexButton")

                        right_thumbstick_x = data.get("rightThumbstickX")
                        right_thumbstick_y = data.get("rightThumbstickY")

                        number_of_collision = data.get("numberOfCollision")
                        head_position = data.get("headPosition")
                        head_rotation = data.get("headRotation")
                        collision_position = data.get("collisionPosition")
                        self.print_important_data(timestamp=timestamp, degree=degree, level=level, feedback_modality=feedback_modality,
                                                  number_of_collision=number_of_collision, interval_number=interval_number)

                        # Log row immediately
                        writer.writerow([
                            timestamp,
                            interval_number,
                            trial_number,
                            is_dynamic_obstacle_present,
                            degree,
                            level,
                            feedback_modality,
                            right_index_button,
                            left_index_button,
                            right_thumbstick_x,
                            right_thumbstick_y,
                            number_of_collision,
                            head_position,
                            head_rotation,
                            # head_pos_x,
                            # head_pos_y,
                            # head_pos_z,
                            # head_rot_x,
                            # head_rot_y,
                            # head_rot_z,
                            collision_position,
                        ])
                        f.flush()

                        if feedback_modality == "haptic" and is_dynamic_obstacle_present:
                            t = 1
                            self.vib.send_vibration_data(degree, level)
                        else:
                            self.vib.send_vibration_data(degree, 10)
                            t = 1
                        if timestamp - self.prev_timestamp > 10 or self.isFirstTimeRecording: # a new part is started
                            self.run_audio_recorder()


                        self.prev_timestamp = timestamp
                    except Exception:
                        print(traceback.format_exc())
                        self.running = False
                        break

        except Exception:
            print("Failed to open log file:")
            print(traceback.format_exc())

    def print_important_data(self, timestamp, degree, level, feedback_modality, number_of_collision, interval_number):
        print(f"Timestamp: {timestamp} | Degree: {degree} | Level: {level} | fb_mod: {feedback_modality} "
              f"| noCollision: {number_of_collision} | intervNo: {interval_number}")

    def run_audio_recorder(self):
        self.isFirstTimeRecording = False
        script_dir = os.path.dirname(os.path.abspath(__file__))
        recorder_path = os.path.join(script_dir, "audio_recorder.py")
        self.experiment_phase += 1
        process = subprocess.Popen([sys.executable, recorder_path])

    def send_dummy_data(self):
        """Send dummy data to server periodically."""
        while self.running:
            try:
                # Send dummy response data
                dummy_response = {'tempFromPCtoHMD': 1}
                send_data_with_prefix(self.client_socket, dummy_response)
                #print(f"Sent dummy data: {dummy_response}")
                time.sleep(10)  # Send every 10 second
            except Exception as e:
                print(traceback.format_exc())
                self.running = False
                break


    def start(self):
        self.read_subject_info()
        """Start the client threads."""
        receiver_thread = threading.Thread(target=self.receive_data, daemon=True)
        receiver_thread.start()
        sender_thread = threading.Thread(target=self.send_dummy_data, daemon=True)
        sender_thread.start()
        # audio_record_thread = threading.Thread(target=self.record_audio, daemon=True)
        # audio_record_thread.start()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False
            if self.client_socket:
                self.client_socket.close()


if __name__ == "__main__":
    client = SimpleClient()
    client.start()