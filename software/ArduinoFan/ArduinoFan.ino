
const bool POWER_INVERTED = false;
const bool PWM_INVERTED = false;

const int POWER_PIN = 11;
const int SENSE_PIN = 12;
const int PWM_PIN = 13;                 // changing this doesn't actually change the PWM pin. See setupPWM.

const int BUFFER_SIZE = 32;
const int RPM_CALC_INTERVAL = 5000;     // milliseconds
const int MAX_PWM_PERIOD = 240;         // set for 25kHz
unsigned long SENSE_DEBOUNCE_TIME = 6;  // milliseconds (6 =~ 2500 rpm max)

bool senseState = true;                 // last sense pin input
bool pulseState = false;                // is the pulse currently high?
unsigned long lastSenseChange = 0;      // last time the sense pin changed
int pulseCount = 0;                     // how many pulses have been counted
unsigned long lastCalcTime = 0;         // last time RPM was calculated
int rpm = 0;                            // last calculated RPM

int dutyCycle = 100;                    // default to full on
char buffer[BUFFER_SIZE] = "";
int bufferPos = 0;

void setup() {
    Serial.begin(9600);
    pinMode(POWER_PIN, OUTPUT);
    pinMode(SENSE_PIN, INPUT_PULLUP);
    
    digitalWrite(POWER_PIN, HIGH);
    
    setupPWM();
    setFan();
    
    Serial.println("READY");
}

/*
    We need special PWM handling because computer fans expect a PWM signal with
    a 25kHz frequency, far beyond the standard 500Hz frequency Arduino Zero's put
    out. There are no Arduino functions for changing the frequency, so direct
    port maniuplation is necessary.

    See https://forum.arduino.cc/t/changing-arduino-zero-pwm-frequency/334231/3
*/
void setupPWM() {
    
    REG_GCLK_GENDIV = GCLK_GENDIV_DIV(4) |          // Divide the 48MHz clock source by divisor 4: 48MHz/4=12MHz
                      GCLK_GENDIV_ID(4);            // Select Generic Clock (GCLK) 4
    while (GCLK->STATUS.bit.SYNCBUSY);              // Wait for synchronization

    REG_GCLK_GENCTRL = GCLK_GENCTRL_IDC |           // Set the duty cycle to 50/50 HIGH/LOW
                       GCLK_GENCTRL_GENEN |         // Enable GCLK4
                       GCLK_GENCTRL_SRC_DFLL48M |   // Set the 48MHz clock source
                       GCLK_GENCTRL_ID(4);          // Select GCLK4
    while (GCLK->STATUS.bit.SYNCBUSY);              // Wait for synchronization

    // To change the PWM pin, these 2 lines need to change. It's complicated. See the linked post.
    
    // D13 = PA17 (odd of PA16 (D11)/PA17 (D13) pair)
    // D7 = PA21 (odd of PA20 (D6)/PA21 (D7) pair)
    // D8 = PA6 (even of PA06 (D8)/PA07 (D9) pair)  can't get this one to work
    
    // Enable the port multiplexer for digital pin 8 (D8): timer TCC0 output
    //PORT->Group[g_APinDescription[7].ulPort].PINCFG[g_APinDescription[7].ulPin].bit.PMUXEN = 1; // D7
    PORT->Group[g_APinDescription[13].ulPort].PINCFG[g_APinDescription[13].ulPin].bit.PMUXEN = 1; // D13
  
    // Connect the TCC0 timer to the port output - port pins are paired odd PMUXO and even PMUXE
    // F = timer TCC0
    // E = timer TCC1 and TCC2
    
    //PORT->Group[g_APinDescription[6].ulPort].PMUX[g_APinDescription[6].ulPin >> 1].reg = PORT_PMUX_PMUXO_F; // D7
    PORT->Group[g_APinDescription[11].ulPort].PMUX[g_APinDescription[11].ulPin >> 1].reg = PORT_PMUX_PMUXO_F; // D13
  
    // Feed GCLK4 to TCC0 and TCC1
    REG_GCLK_CLKCTRL = GCLK_CLKCTRL_CLKEN |         // Enable GCLK4 to TCC0 and TCC1
                       GCLK_CLKCTRL_GEN_GCLK4 |     // Select GCLK4
                       GCLK_CLKCTRL_ID_TCC0_TCC1;   // Feed GCLK4 to TCC0 and TCC1
    while (GCLK->STATUS.bit.SYNCBUSY);              // Wait for synchronization

    // Dual slope PWM operation: timers countinuously count up to PER register value then down 0
    REG_TCC0_WAVE |= TCC_WAVE_POL(0xF) |            // Reverse the output polarity on all TCC0 outputs
                     TCC_WAVE_WAVEGEN_DSBOTH;     // Setup dual slope PWM on TCC0
    while (TCC0->SYNCBUSY.bit.WAVE);                // Wait for synchronization

    // Each timer counts up to a maximum or TOP value set by the PER register,
    // this determines the frequency of the PWM operation:
    REG_TCC0_PER = MAX_PWM_PERIOD;                  // Set the frequency of the PWM on TCC0 to 25kHz
    while(TCC0->SYNCBUSY.bit.PER);

    // Divide the 12MHz signal by 1 giving 12MHz TCC0 timer tick and enable the outputs
    REG_TCC0_CTRLA |= TCC_CTRLA_PRESCALER_DIV1 |    // Divide GCLK4 by 1
                      TCC_CTRLA_ENABLE;             // Enable the TCC0 output
    while (TCC0->SYNCBUSY.bit.ENABLE);              // Wait for synchronization
}

void setPWMDutyCycle(int dc) {
    // 0 <= dc <= MAX_PWM_PERIOD
    // Set the PWM signal to output duty cycle
    REG_TCC0_CCB3 = dc;
    while(TCC0->SYNCBUSY.bit.CCB3);
}

void loop() {
    countPulses();

    if (Serial.available() > 0)
        readCommand();
    
    if ((millis() - lastCalcTime) >= RPM_CALC_INTERVAL)
        calculateRPM();
}

void countPulses() {
    bool in = digitalRead(SENSE_PIN) == HIGH;
    if (in != senseState) {
        lastSenseChange = millis();
        senseState = in;
    }
    
    if ((millis() - lastSenseChange) > SENSE_DEBOUNCE_TIME) {
        if (pulseState) {
            if (! senseState)
                pulseState = false;
        } else {
            if (senseState) {
                pulseCount++;
                pulseState = true;
            }
        }
    }
}

void readCommand() {
    int ch = Serial.read();
    while (ch != -1) {
        if ((ch == '\r') || (ch == '\n')) {
            buffer[bufferPos] = 0;
            if (bufferPos > 0) {
                processCommand();
                bufferPos = 0;
            }
        } else {
            buffer[bufferPos++] = ch;
            if (bufferPos == BUFFER_SIZE) {
                bufferPos = 0;
                Serial.println("OVERFLOW");
            }
        }
        ch = Serial.read();
    }
}

void processCommand() {
    String str = String(buffer);
    int pos = str.indexOf(' ');
    if (pos == -1) {
        // single word commands
        if (str.equalsIgnoreCase("RPM")) {
            Serial.print("RPM ");
            Serial.println(rpm);
            return;
        }
        if (str.equalsIgnoreCase("DUTYCYCLE")) {
            Serial.print("DUTYCYCLE ");
            Serial.println(dutyCycle);
            return;
        }
        Serial.println("UNKNOWN COMMAND");
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
            Serial.println("OK");
        } else
            Serial.println("INVALID ARGUMENT");
        return;
    }
    Serial.println("UNKNOWN COMMAND");
}

void calculateRPM() {
    int pc = pulseCount;
    pulseCount = 0;
    float sec = (float)(millis() - lastCalcTime) / 1000.0f;
    lastCalcTime = millis();
    
    float pps = (float)pc / sec;
    // fans pulse 2 times per revolution
    rpm = (int)(30.0f * pps);
    //Serial.print("pc=");
    //Serial.print(pc);
    //Serial.print(", pps=");
    //Serial.print(pps);
    //Serial.print(", rpm=");
    //Serial.println(rpm);
    //return;
    Serial.print("RPM ");
    Serial.println(rpm);
}

void setFan() {
    if (dutyCycle == 0) {   // fan is off
        if (POWER_INVERTED) {
            digitalWrite(POWER_PIN, HIGH);
        } else {
            digitalWrite(POWER_PIN, LOW);
        }
        if (PWM_INVERTED) {
            setPWMDutyCycle(MAX_PWM_PERIOD);
        } else {
            setPWMDutyCycle(0);
        }
        
    } else {
        // convert to 0-MAX_PWM_PERIOD
        int dc = (int)(((float)dutyCycle / 100) * (float)MAX_PWM_PERIOD);
        if (POWER_INVERTED) {
            digitalWrite(POWER_PIN, LOW);
        } else {
            digitalWrite(POWER_PIN, HIGH);
        }
        if (PWM_INVERTED) {
            setPWMDutyCycle(MAX_PWM_PERIOD - dc);
        } else {
            setPWMDutyCycle(dc);
        }
    }
}
    