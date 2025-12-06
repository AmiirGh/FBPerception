int val = 0;
int buzzer = 6;
void setup() {
  // put your setup code here, to run once:
  pinMode(buzzer, OUTPUT);
}

void loop() {
  analogWrite(buzzer, 1);
  delay(3000);
  analogWrite(buzzer, 150);
  delay(3000);
  analogWrite(buzzer, 240);
  delay(3000);

}
