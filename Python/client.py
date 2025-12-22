import socket
import json
import time
import struct
import threading
import traceback
from vibration import *

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
    def __init__(self, host='192.168.0.105', port=12345):
        self.client_socket = None
        self.running = True
        self.connect_to_server(host, port)
        self.vib = VibrationClient()
        self.invalid_degree_int = 10
        self.invalid_level = 10
        # Send initial dummy data
        send_data_with_prefix(self.client_socket, {'tempFromPCtoHMD': 1})

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
        """Receive data from server in a separate thread."""
        while self.running:
            try:
                data = receive_data_with_prefix(self.client_socket)
                if data:
                    timestamp = data.get('timestamp')
                    interval_number = data.get('intervalNumber')
                    trial_number = data.get('trialNumber')
                    is_dynamic_obstacle_present = data.get('isDynamicObstaclePresent')
                    extra_fb_modality = data.get('extraFbModality')
                    degree = data.get('degree')
                    degree_int = data.get('degreeInt')
                    level = data.get('level')
                    is_haptic_feedback = data.get('isHapticFeedback')
                    right_index_button = data.get('rightIndexButton')

                    print(f"is present: {is_dynamic_obstacle_present} |  is haptic: {is_haptic_feedback}")

                    if is_haptic_feedback and is_dynamic_obstacle_present:
                        #as long as that the dynamic obstacle  is present and feedback is haptic sends vibration
                        self.vib.send_vibration_data(degree_int, level)
                    else:
                        self.vib.send_vibration_data(degree_int, 10) # 10 means unspecified and means turn it off

                    # print(f"Received data: {data}")
            except Exception as e:
                print(traceback.format_exc())
                self.running = False
                break

    def send_dummy_data(self):
        """Send dummy data to server periodically."""
        while self.running:
            try:
                # Send dummy response data
                dummy_response = {'tempFromPCtoHMD': 1}
                send_data_with_prefix(self.client_socket, dummy_response)
                print(f"Sent dummy data: {dummy_response}")
                time.sleep(10)  # Send every second
            except Exception as e:
                print(traceback.format_exc())
                self.running = False
                break

    def start(self):
        """Start the client threads."""
        receiver_thread = threading.Thread(target=self.receive_data, daemon=True)
        receiver_thread.start()
        sender_thread = threading.Thread(target=self.send_dummy_data, daemon=True)
        sender_thread.start()

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
