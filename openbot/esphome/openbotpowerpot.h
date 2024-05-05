#include "esphome.h"

/*
#include "Arduino.h"
#include "component.h"
#include "sensor/sensor.h"
#include "output/float_output.h"

using namespace esphome;
using namespace esphome::sensor;
using namespace esphome::output;
*/

class TrackingFloatOutput : public FloatOutput {
 public:
  float state;

  TrackingFloatOutput() : FloatOutput() {}

  void write_state(float state) override {
    this->state = state;
  }
};

class TrackingBinaryOutput : public BinaryOutput {
 public:
  bool state;

  TrackingBinaryOutput() : BinaryOutput() {}

  void write_state(bool state) override {
    this->state = state;
  }
};

class OpenbotMainRead : public PollingComponent {
 public:
  //Sensor *position_sensor = new Sensor();
  TrackingFloatOutput *position_target = new TrackingFloatOutput();
  TrackingFloatOutput *target_enable = new TrackingFloatOutput();

  OpenbotMainRead(uint8_t pot_pin, uint8_t fwd_pin,
    uint8_t rev_pin, int allowed_varance, int sleepSteps)
      : PollingComponent(10000), pot_pin(pot_pin),
      fwd_pin(fwd_pin), rev_pin(rev_pin),
      allowed_varance(allowed_varance),
      sleepSteps(sleepSteps) {}

  void setup() override {
    pinMode(pot_pin, INPUT);
    pinMode(fwd_pin, OUTPUT);
    pinMode(rev_pin, OUTPUT);
  }

  // Part of PollingComponent; called every [time] to read pot
  void update() override {
    //int currentPos = analogRead(A0);
    //position_sensor->publish_state(currentPos);
  }

  void loop() override {
    if (target_enable->state && (proc=(proc+1)%sleepSteps) == 1) {
      int currentPos = analogRead(A0);
      int targetPos = (int)(position_target->state*1024.0);
      // Close fast
      if (abs(currentPos-targetPos) <= allowed_varance) {
        digitalWrite(fwd_pin, 0);
        digitalWrite(rev_pin, 0);
        return;
      }
      if (currentPos > targetPos) {
        digitalWrite(fwd_pin, 0);
        digitalWrite(rev_pin, 1);
      } else {
        digitalWrite(rev_pin, 0);
        digitalWrite(fwd_pin, 1);
      }
    }
  }

 private:
  uint8_t pot_pin;
  uint8_t fwd_pin;
  uint8_t rev_pin;
  int allowed_varance;
  uint8_t proc = 0;
  int sleepSteps;
};

class BetterADC: public Component, public Sensor {
 public:
  BetterADC(uint8_t pin, int delta, int smooth, int sleepSteps): Component(), Sensor(), pin(pin), delta(delta), smooth(smooth), sleepSteps(sleepSteps) {}

  void setup() override {
    pinMode(pin, INPUT);
    lastValue = analogRead(pin);
    accum = lastValue;
  }

  void loop() override {
    if ((proc=(proc+1)%sleepSteps) == 0) {
      int val = analogRead(pin);
      accum = (accum*(smooth-1) + val)/smooth;
      if (abs(accum - lastValue) > delta) {
        publish_state(accum);
        lastValue = accum;
      }
    }
  }

 private:
  int accum;
  uint8_t pin;
  int lastValue;
  int delta;
  int smooth;
  uint8_t proc = 0;
  int sleepSteps;
};