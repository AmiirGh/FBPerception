const int BUZZER_PIN = 6;  // I've used your original pin 6
const int TONE_FREQ = 1000; // Choose a clear frequency, e.g., 1000 Hz

int incoming_level = 0;   // The level received from Unity (0, 1, 2, or 3)

// --- Intensity Values ---
const int LOW_INTENSITY = 1; //1
const int MED_INTENSITY = 10; //3
const int HIGH_INTENSITY = 70; //10
int CUR_INTENSITY = 0;
// ------------------------

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) 
  { 
    char cmd = Serial.read();
    if (cmd == '0') 
    {
      analogWrite(BUZZER_PIN, LOW_INTENSITY);
    } 
    else if (cmd == '1') 
    {
      analogWrite(BUZZER_PIN, MED_INTENSITY);
    } 
    else if (cmd == '2') 
    {
      analogWrite(BUZZER_PIN, HIGH_INTENSITY);
    } 

  }
}