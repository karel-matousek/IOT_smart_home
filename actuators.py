import sys
sys.path.append("/")
from generic.lamp import Lamp
from machine import Pin
from time import ticks_ms, ticks_diff
from generic import config
from generic.wifi import initialize_wifi
from generic.umqtt import implementation as mqtt
from generic.umqtt.implementation import MQTT_TOPIC_LAMP, MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_ALARM, MQTT_TOPIC_TEMPERATURE_SETPOINT, MQTT_TOPIC_HEATER
from generic.my_print import my_print
from generic.buzzer import Buzzer
from generic.heater import Heater

# === Objects
wlan = None
client = None
lamp = Lamp(pin="LED")
buzzer = Buzzer(18, duty=30000, freq=2000, period_on_ms=150, period_off_ms=150)
heater = Heater(28)

# === Timing variables
terminal_print_period_ms = 1000
terminal_print_prev_time = 0

# === Constants
MQTT_CLIENT_ID = b"actuator_picow"

def mqtt_received_callback(topic, message):
    topic = topic.decode('utf-8')
    message = message.decode('utf-8')

    my_print(f"Received message on topic: {topic}, response: {message}")

    if topic == MQTT_TOPIC_ALARM:
        if message == 'ON':
            my_print('Alarm ON')
            buzzer.state = True
        elif message == 'OFF':
            my_print('Alarm OFF')
            buzzer.state = False
        else:
            my_print('Unknown command for alarm')

    elif topic == MQTT_TOPIC_LAMP:
        if message == 'ON':
            my_print('Turning LED ON')
            lamp.state = True
        elif message == 'OFF':
            my_print('Turning LED OFF')
            lamp.state = False
        else:
            my_print('Unknown command for lamp')

    elif topic == MQTT_TOPIC_HEATER:
        if message == 'ON':
            my_print('Turning heater ON')
            heater.state = True
        elif message == 'OFF':
            my_print('Turning heater OFF')
            heater.state = False
        else:
            my_print('Unknown command for heater')

    else:
        my_print('Unknown topic received')

def print_info():
    my_print("=================================================================")
    print(f"\tHeater: \tstate: {'ON' if heater.state else 'OFF'}")
    print(f"\tLamp: \t\tstate: {'ON' if lamp.state else 'OFF'}")
    print(f"\tAlarm: \t\tstate: {'ON' if buzzer.state else 'OFF'}")

try:
    print("=== Actuators =============================================================")

    wlan = initialize_wifi(config.wifi_ssid, config.wifi_password)
    if not wlan:
        raise Exception('WiFi connection failed')
    my_print('Connected to WiFi successfully!')
    
    client = mqtt.connect_mqtt(MQTT_CLIENT_ID)
    if not client:
        raise Exception('MQTT connection failed')
    my_print('Connected to MQTT broker successfully!')

    client.set_callback(mqtt_received_callback)
    mqtt.subscribe(client, MQTT_TOPIC_LAMP)
    mqtt.subscribe(client, MQTT_TOPIC_ALARM)
    mqtt.subscribe(client, MQTT_TOPIC_HEATER)

    while True:
        client.check_msg()

        buzzer.update()
        lamp.update()
        heater.update()

        if ticks_diff(ticks_ms(), terminal_print_prev_time) >= terminal_print_period_ms:
            terminal_print_prev_time = ticks_ms()
            print_info()
        
except Exception as e:
    my_print('Error:', e)

finally:
    lamp.state = False
    lamp.update()

    buzzer.state = False
    buzzer.update()

    heater.state = False
    heater.update()

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