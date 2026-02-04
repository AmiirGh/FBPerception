#include <WiFi.h>

//const char* ssid = "RAIIS";
const char* ssid = "Amir_Gh";
// const char* ssid = "UT-WiFi";
// const char* password = "11111111";

const char* password = "amir1234";
bool pinActive = false;
unsigned long triggerTime = 0;
// const unsigned long pulseDuration = 150;  // 150 ms pulse


// Set the server port
const uint16_t port = 12345;
WiFiServer server(port);

const int VIBRATOR_LEFT = 19;
const int VIBRATOR_BACK = 26;
const int VIBRATOR_RIGHT = 23;
const int VIBRATOR_FRONT = 27;

volatile bool dataReceivedInterrupt = false;

const int freq = 5000; 
const int ledChannel = 0;
const int resolution = 8;
void setup() {
  Serial.begin(115200);
  Serial.println("\ntrying to connect");
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(10);
    Serial.print(".");
  }
  Serial.println("\nConnected to the WiFi network");

  server.begin();
  Serial.println("Server started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  ledcAttach(VIBRATOR_LEFT , freq , resolution);
  ledcAttach(VIBRATOR_BACK , freq , resolution);
  ledcAttach(VIBRATOR_RIGHT , freq , resolution);
  ledcAttach(VIBRATOR_FRONT , freq , resolution);

}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    while (client.connected()) {
      if (client.available() >= 4) {
        uint8_t data[4];
        client.read(data, 4);


        ledcWrite(VIBRATOR_FRONT, data[1]);
        ledcWrite(VIBRATOR_RIGHT, data[0]);
        ledcWrite(VIBRATOR_BACK, data[3]);
        ledcWrite(VIBRATOR_LEFT, data[2]);

        // ledcWrite(ledPin4, data[1]);
        // ledcWrite(ledPin3, data[0]);
        // ledcWrite(ledPin2, data[3]);
        // ledcWrite(ledPin, data[2]);

      }
    }
    client.stop();
    Serial.println("Client disconnected");
  }
}