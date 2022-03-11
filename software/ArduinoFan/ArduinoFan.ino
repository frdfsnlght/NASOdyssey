
const bool PWM = true;
const bool POWER_INVERTED = false;
const bool PWM_INVERTED = false;
const bool PWM_ON_POWER = false;

const int POWER_PIN = 11;
const int SENSE_PIN = 12;
const int PWM_PIN = 13;

const int BUFFER_SIZE = 32;
const int CALC_INTERVAL = 1000;  // milliseconds

int dutyCycle = 0;
int pulseCount = 0;
int rpm = 0;
unsigned long lastCalcTime = 0;
char buffer[BUFFER_SIZE] = "";
int bufferPos = 0;

void setup() {
    Serial.begin(115000);
    pinMode(POWER_PIN, OUTPUT);
    pinMode(SENSE_PIN, INPUT_PULLUP);
    pinMode(PWM_PIN, OUTPUT);
    
    setFan();
    
    attachInterrupt(digitalPinToInterrupt(SENSE_PIN), countPulse, FALLING);
    
    interrupts();
    
    Serial.print("READY\n");
}

void loop() {
    if (Serial.available() > 0)
        readCommand();
    
    if ((millis() - lastCalcTime) >= CALC_INTERVAL)
        calculateRPM();
}

void countPulse() {
    pulseCount++;
}

void readCommand() {
    while (int ch = Serial.read() != -1) {
        if (ch == '\r') continue; // ignore carriage return
        if (ch == '\n') {
            buffer[bufferPos] = 0;
            if (bufferPos > 0) {
                processCommand();
                bufferPos = 0;
            }
        } else {
            buffer[bufferPos++] = ch;
            if (bufferPos == BUFFER_SIZE) {
                bufferPos = 0;
                Serial.print("OVERFLOW\n");
            }
        }
    }
}

void processCommand() {
    String str = String(buffer);
    int pos = str.indexOf(' ');
    if (pos == -1) {
        // single word commands
        Serial.print("UNKNOWN COMMAND\n");
        return;
    }
    String cmd = str.substring(0, pos);
    String args = str.substring(pos);
    if (cmd.equalsIgnoreCase("DUTYCYCLE")) {
        // args is new duty cycle integer, 0-100
        int dc = args.toInt();
        if ((dc >= 0) && (dc <= 100)) {
            dutyCycle = dc;
            setFan();
        } else
            Serial.print("INVALID ARGUMENT\n");
        return;
    }
    Serial.print("UNKNOWN COMMAND\n");
}

void calculateRPM() {
    float pps = (float)pulseCount / ((float)(millis() - lastCalcTime) / 1000.0f);
    pulseCount = 0;
    lastCalcTime = millis();
    // fans pulse 2 times per revolution
    int newRPM = (int)(30.0f * pps);
    if (newRPM != rpm) {
        rpm = newRPM;
        Serial.print("RPM ");
        Serial.print(rpm);
        Serial.print('\n');
    }
}

void setFan() {
    if (dutyCycle == 0) {   // fan is off
        if (POWER_INVERTED)
            digitalWrite(POWER_PIN, HIGH);
        else
            digitalWrite(POWER_PIN, LOW);
        if (PWM) {
            if (PWM_INVERTED)
                analogWrite(PWM_PIN, 255);
            else
                analogWrite(PWM_PIN, 0);
        }
        
    } else if (! PWM) {
        // just turn the fan on
        if (POWER_INVERTED)
            digitalWrite(POWER_PIN, LOW);
        else
            digitalWrite(POWER_PIN, HIGH);
        
    } else {
        // convert to 0-255
        int dc = (int)(((float)dutyCycle / 100) * 255.0f);
        if (PWM_ON_POWER) {
            if (POWER_INVERTED)
                analogWrite(POWER_PIN, 255 - dc);
            else
                analogWrite(POWER_PIN, dc);
        } else {
            if (POWER_INVERTED)
                digitalWrite(POWER_PIN, LOW);
            else
                digitalWrite(POWER_PIN, HIGH);
            if (PWM_INVERTED)
                analogWrite(PWM_PIN, 255 - dc);
            else
                analogWrite(PWM_PIN, dc);
        }
    }
}
    