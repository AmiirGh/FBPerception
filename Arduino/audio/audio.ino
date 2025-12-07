// Using Arduino Mege. Pins 2 to 13 are PWM
const int BUZZER_RIGHT = 2;
const int BUZZER_FRONT = 6;
const int BUZZER_LEFT = 10;
const int BUZZER_BACK = 12;


const int TONE_FREQ = 1000; // Choose a clear frequency, e.g., 1000 Hz

int incoming_level = 0;   // The level received from Unity (0, 1, 2, or 3)

// --- Intensity Values ---
const int LOW_INTENSITY = 1; //1
const int MED_INTENSITY = 3; //3
const int HIGH_INTENSITY = 30; //10
int PREV_INTENSITY = 150;
int intensity = 0;
// ------------------------
int GetIntensity(int level)
{
  intensity = 0;
  if (level == 0) intensity = HIGH_INTENSITY;

  else if (level == 1) intensity = MED_INTENSITY;

  else if (level == 2) intensity = LOW_INTENSITY;
  return intensity;
}
void setup() {
  pinMode(BUZZER_FRONT, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0)
  {
    String inputString = Serial.readStringUntil('\n');
    Serial.println("S.th");
    if (inputString.length() > 0) 
    {
      int commaIndex = inputString.indexOf(',');
      if (commaIndex != -1) 
      {
        String levelString = inputString.substring(0, commaIndex);
        String degreeString = inputString.substring(commaIndex + 1);

        int level = levelString.toInt();
        int degree = degreeString.toInt();

        if (degree == 0)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_RIGHT, intensity);
        }

        else if (degree == 1)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_RIGHT, intensity);
          analogWrite(BUZZER_FRONT, intensity);
        }
        else if (degree == 2)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_RIGHT, intensity);
          analogWrite(BUZZER_FRONT, intensity);
        }
        else if (degree == 3)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_FRONT, intensity);
          analogWrite(BUZZER_LEFT, intensity);
        }
        else if (degree == 4)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_LEFT, intensity);
        }
        else if (degree == 5)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_LEFT, intensity);
          analogWrite(BUZZER_BACK, intensity);
        }
        else if (degree == 6)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_BACK, intensity);
        }
        else if (degree == 7)
        {
          intensity = GetIntensity(level);
          analogWrite(BUZZER_RIGHT, intensity);
          analogWrite(BUZZER_BACK, intensity);
        }




        delay(500);
      }
    }
  }


}



