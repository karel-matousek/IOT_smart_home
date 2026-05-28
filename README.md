# IOT_smart_home

## Assignment
Program several devices for smart home control.

For realization utilize:
- Control gateway - Manages the desired actions based on data received from sensors.
- Sensors - Measure and transmit data  
- Actuators - Based on received commands execute the desired actions

## Realization
Sensor board collects data about the temperature using AHT20 sensor communicating via I2C, reads a state of a button for light switching and simulates an intruder alert also using a button. The information about the light switch and intruder alert is sent directly to the actuator board. The measured temperature is sent to gateway which decides whether to turn the heater on or off and sends a relevant command to the actuator board. The heater logic uses hysteresis to avert ceaseless on/off swithing. The desired temperature can be set through the gateway.