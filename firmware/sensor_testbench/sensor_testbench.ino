/*
  Embedded Sensor Testbench

  Streams analog sensor readings as CSV for a Python validation tool.
  Hardware:
    - Arduino Uno or compatible board
    - Potentiometer or analog sensor output connected to A0
    - Shared ground between sensor and Arduino
*/

const int SENSOR_PIN = A0;
const int STATUS_LED_PIN = LED_BUILTIN;

const unsigned long SAMPLE_PERIOD_MS = 20;
const float ADC_REFERENCE_MV = 5000.0;
const float ADC_MAX_COUNT = 1023.0;
const float FILTER_ALPHA = 0.18;
const float DIGITAL_THRESHOLD_MV = 2500.0;

unsigned long lastSampleMs = 0;
unsigned long sampleId = 0;
float filteredMv = 0.0;
bool filterReady = false;

float adcToMillivolts(int rawAdc) {
  return (rawAdc * ADC_REFERENCE_MV) / ADC_MAX_COUNT;
}

void printHeader() {
  Serial.println("sample_id,timestamp_ms,raw_adc,voltage_mv,filtered_mv,digital_state");
}

void setup() {
  pinMode(STATUS_LED_PIN, OUTPUT);
  Serial.begin(115200);

  while (!Serial) {
    ; // Wait for native USB boards.
  }

  printHeader();
}

void loop() {
  const unsigned long nowMs = millis();
  if (nowMs - lastSampleMs < SAMPLE_PERIOD_MS) {
    return;
  }

  lastSampleMs = nowMs;

  const int rawAdc = analogRead(SENSOR_PIN);
  const float voltageMv = adcToMillivolts(rawAdc);

  if (!filterReady) {
    filteredMv = voltageMv;
    filterReady = true;
  } else {
    filteredMv = (FILTER_ALPHA * voltageMv) + ((1.0 - FILTER_ALPHA) * filteredMv);
  }

  const int digitalState = filteredMv >= DIGITAL_THRESHOLD_MV ? 1 : 0;
  digitalWrite(STATUS_LED_PIN, digitalState == 1 ? HIGH : LOW);

  Serial.print(sampleId++);
  Serial.print(',');
  Serial.print(nowMs);
  Serial.print(',');
  Serial.print(rawAdc);
  Serial.print(',');
  Serial.print(voltageMv, 2);
  Serial.print(',');
  Serial.print(filteredMv, 2);
  Serial.print(',');
  Serial.println(digitalState);
}
