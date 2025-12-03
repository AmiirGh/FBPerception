import struct
import socket
import time

class VibrationClient:
    def __init__(self, esp32_ip="192.168.0.116", port=12345):
        """
        Initializes the VibrationClient with a persistent connection.
        Args:
        - esp32_ip: The IP address of the ESP32 device.
        - port: The port number to connect to.
        """
        self.esp32_ip = esp32_ip
        self.port = port
        self.client_socket = None
        self.connect()

    def connect(self):
        """Establishes a persistent connection to the ESP32 with retries."""
        try:
            if self.client_socket is None:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.settimeout(5)  # Timeout for connection attempts
                self.client_socket.connect((self.esp32_ip, self.port))
                print("------------------")
                print("Connected to ESP32")
                print("------------------")
        except (socket.error, socket.timeout) as e:
            print("/////////////////////////")
            print(f"Connection failed: {e}")
            print("////////////////////")
            self.client_socket = None

    def send_vibration_data(self, intensity):
        """
        Sends vibration data based on the given intensity.
        Automatically reconnects if disconnected.
        
        Args:
        - intensity: The intensity value (0-255)
        """
        if self.client_socket is None:
            print("Reconnecting...")
            self.connect()

        if self.client_socket:
            try:
                byte_data = struct.pack('4B', intensity, 0, intensity, 0)
                self.client_socket.sendall(byte_data)
                print(f"Vibration triggered with intensity {intensity}")
            except (socket.error, BrokenPipeError):
                print("Connection lost. Attempting to reconnect...")
                self.client_socket = None
                self.connect()

    def stop_vibration(self):
        """Sends a stop vibration signal and attempts to reconnect if necessary."""
        if self.client_socket is None:
            print("Reconnecting...")
            self.connect()

        if self.client_socket:
            try:
                self.client_socket.sendall(struct.pack('4B', 0, 0, 0, 0))  # Stop signal
                # print("Vibration stopped")
            except (socket.error, BrokenPipeError):
                print("Connection lost while stopping vibration. Reconnecting...")
                self.client_socket = None
                self.connect()

    def close(self):
        """Closes the persistent connection safely."""
        if self.client_socket:
            try:
                self.client_socket.sendall(struct.pack('4B', 0, 0, 0, 0))  # Stop signal
                print("Turn off signal sent")
                time.sleep(1)
                self.client_socket.close()
            except socket.error:
                print("Error while closing connection")
            finally:
                self.client_socket = None
                print("Connection closed")

# Example Usage:
if __name__ == "__main__":
    vibration_client = VibrationClient()
    vibration_client.send_vibration_data(120)
    time.sleep(3)
    vibration_client.stop_vibration()

