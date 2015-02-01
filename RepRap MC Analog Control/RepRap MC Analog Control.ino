/* Pins */
#define VRX A0
#define VRY A1
#define KEYBOARD_OUTPUT 4
#define EXTRUDE_BUTTON 3
#define PLATE_BUTTON 2

#define DELAY_POLL 20

int joystick_zero = 1024 / 2;
int tolerance = 30;

int upper_bound = joystick_zero + tolerance;
int lower_bound = joystick_zero - tolerance;

int X, Y;
long extrude = 0, plate = 0;
int number_of_samples = 50; // The number of samples we use for deboucing the buttons

void setup() {
  
  pinMode(VRX, INPUT);
  pinMode(VRY, INPUT);
  
  pinMode(KEYBOARD_OUTPUT, OUTPUT);
  pinMode(PLATE_BUTTON, INPUT_PULLUP);
  pinMode(EXTRUDE_BUTTON, INPUT_PULLUP);

  // Send a LOW for the button matrix
  digitalWrite(KEYBOARD_OUTPUT, LOW);
  
  Serial.begin(115200);
  
}

void loop() {
  

  // Read all values from the joystick
  X = analogRead(VRX); // will be 0-1023
  Y = analogRead(VRY); // will be 0-1023

  // Reset counters
  extrude = 0, plate = 0;
  
  for (int i = 0; i<number_of_samples; i++) {
    extrude += int(digitalRead(EXTRUDE_BUTTON)); // will be HIGH (1) if not pressed, and LOW (0) if pressed
  }
  extrude = ceil(extrude / number_of_samples);
  
  for (int i = 0; i<number_of_samples; i++) {
    plate += int(digitalRead(PLATE_BUTTON)); // will be HIGH (1) if not pressed, and LOW (0) if pressed
  }
  plate = ceil(plate / number_of_samples);
  
  // If there is something happening
  if (X < lower_bound || X > upper_bound || Y < lower_bound || Y > upper_bound || extrude == 0 || plate == 0) {
    
    Serial.print(X, DEC);
    Serial.print(",");
    
    Serial.print(Y, DEC);
    Serial.print(",");
    
    if (extrude == 1) {
      Serial.print("0,");//Serial.println("not pressed");
    } else {
      Serial.print("1,");
    }
    
    if (plate == 1) {
      Serial.println("0");//Serial.println("not pressed");
    } else {
      Serial.println("1");
    }

  }
  
  delay(DELAY_POLL);

}
