import sys
sys.path.append("/")
import machine
import time
from generic import config
from generic.wifi import initialize_wifi
from generic.umqtt import implementation as mqtt
from generic.umqtt.implementation import MQTT_TOPIC_LAMP, MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_ALARM, MQTT_TOPIC_TEMPERATURE_SETPOINT, MQTT_TOPIC_HEATER
from generic.my_print import my_print
import generic.aht20 as aht20

DEVICE_ADDR = 56
period = 3000

client = None
wlan = None

# Buttons
lamp = machine.Pin(20, machine.Pin.IN)
alarm = machine.Pin(21, machine.Pin.IN)
last_state_alarm = alarm.value()
last_state_lamp = lamp.value()

alarm_last_time = 0
lamp_last_time = 0
temperature_last_time = 0

MQTT_UPLOAD_PERIOD = 30000

# ADHT20
i2c_handle = machine.I2C(0, scl = 1, sda = 0, freq = 100000)
#print(i2c_handle.scan())

sensor = aht20.TMPSensor(i2c_handle, DEVICE_ADDR)
sensor.measure()

MQTT_CLIENT_ID = b"sensors_picow"

try:
    print("=== Sensors =============================================================")

    wlan = initialize_wifi(config.wifi_ssid, config.wifi_password)
    if not wlan:
        raise Exception('WiFi connection failed')
    my_print('Connected to WiFi successfully!')

    client = mqtt.connect_mqtt(MQTT_CLIENT_ID)
    if not client:
        raise Exception('MQTT connection failed')
    my_print('Connected to MQTT broker successfully!')
        
    while True:
        
        if time.ticks_diff(time.ticks_ms(), temperature_last_time) >= 5000:
            temperature_last_time = time.ticks_ms()
            sensor.measure()
            temperature_str = "{:.2f}".format(sensor.temp)
            client.publish(MQTT_TOPIC_TEMPERATURE, temperature_str)
            my_print(f'TEMPERATURE: {temperature_str}')
        #client.publish(MQTT_TOPIC_HUMIDITY, str(sensor.hum))

        #print(sensor.hum)
        #print(sensor.temp)

        # Detect change
        current_state_lamp = lamp.value()
        if current_state_lamp != last_state_lamp or time.ticks_diff(time.ticks_ms(), lamp_last_time) >= MQTT_UPLOAD_PERIOD:
            last_state_lamp = current_state_lamp
            lamp_last_time = time.ticks_ms()
            if current_state_lamp:
                client.publish(MQTT_TOPIC_LAMP, "OFF")
                my_print("LAMP: OFF")
            else:
                client.publish(MQTT_TOPIC_LAMP, "ON")
                my_print("LAMP: ON")
                
        current_state_alarm = alarm.value()
        if current_state_alarm != last_state_alarm or time.ticks_diff(time.ticks_ms(), alarm_last_time) >= MQTT_UPLOAD_PERIOD:
            last_state_alarm = current_state_alarm
            alarm_last_time = time.ticks_ms()
            
            if current_state_alarm:
                client.publish(MQTT_TOPIC_ALARM, "OFF")
                my_print("ALARM: OFF")
            else:
                client.publish(MQTT_TOPIC_ALARM, "ON")
                my_print("ALARM: ON")                
        
except Exception as e:
    my_print('Error:', e)
    
finally:
    if client is not None:
        try:
            client.disconnect()
        except:
            pass

    if wlan is not None:
        try:
            wlan.disconnect()
            wlan.active(False)
        except:
            pass
