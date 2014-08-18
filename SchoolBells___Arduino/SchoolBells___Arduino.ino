const byte noSerialLed = 13;
const byte noSerialBlinkDelay = 50;
const byte bellPin = 2;

void setup() 
{
    pinMode(noSerialLed, OUTPUT);
    pinMode(bellPin, OUTPUT);

    Serial.begin(9600);
    while (!Serial)
    {
        digitalWrite(noSerialLed, HIGH);
        delay(noSerialBlinkDelay);
        digitalWrite(noSerialLed, LOW);
        delay(noSerialBlinkDelay);
    }
}

void loop()
{
    if (Serial.available())
    {
        char controlChar = (char)Serial.read();
        if (controlChar == 'r')
        {
            digitalWrite(bellPin, HIGH);
        }
        else if (controlChar == 's')
        {
            digitalWrite(bellPin, LOW);
        }
    }
}


