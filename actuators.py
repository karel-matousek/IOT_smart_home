import sys
sys.path.append("/")
from machine import Pin
from time import ticks_ms, ticks_diff
from generic import config
from generic.wifi import initialize_wifi
from generic.umqtt import implementation as mqtt
from generic.umqtt.implementation import MQTT_TOPIC_LAMP, MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_ALARM, MQTT_TOPIC_TEMPERATURE_SETPOINT, MQTT_TOPIC_HEATER
from generic.my_print import my_print
from generic.buzzer import Buzzer
from generic.heater import Heater

# === Shared variables
shared = {'mqtt_topic_update_flag': False}

# === Objects
wlan = None
client = None
led = Pin("LED", Pin.OUT)
buzzer = Buzzer(18, duty=30000, freq=2000, period_on_ms=150, period_off_ms=150)
heater = Heater(2, shared=shared)
lamp_state = False

# === Timing variables
mqtt_period_ms = 50000
mqtt_upload_prev_time = 0
#
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
        global lamp_state
        if message == 'ON':
            my_print('Turning LED ON')
            lamp_state = True
        elif message == 'OFF':
            my_print('Turning LED OFF')
            lamp_state = False
        else:
            my_print('Unknown command for lamp')

    elif topic == MQTT_TOPIC_TEMPERATURE_SETPOINT:
        try:
            new_setpoint = float(message)
            heater.setpoint_dC = new_setpoint
            my_print(f'Updated temperature setpoint to {new_setpoint:.2f} °C')
        except ValueError:
            my_print('Invalid temperature setpoint received')

    elif topic == MQTT_TOPIC_TEMPERATURE:
        try:
            new_temperature = float(message)
            heater.current_temperature_dC = new_temperature
            my_print(f'Updated current temperature to {new_temperature:.2f} °C')
        except ValueError:
            my_print('Invalid temperature value received')

    else:
        my_print('Unknown topic received')

def update_lamp():
    if lamp_state == True:
        led.value(1)
    elif lamp_state == False:
        led.value(0)

def print_info():
    my_print("=================================================================")
    print(f"\tTemperature: {heater.current_temperature_dC:.2f} °C")
    print(f"\tHeater: \tstate: {'ON' if heater.state else 'OFF'} \tsetpoint: {heater.setpoint_dC:.2f} °C \thysteresis: {heater.hysteresis_dC:.2f} °C")
    print(f"\tLamp: \t\tstate: {'ON' if lamp_state else 'OFF'}")
    print(f"\tAlarm: \t\tstate: {'ON' if buzzer.state else 'OFF'}")

try:
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
    mqtt.subscribe(client, MQTT_TOPIC_TEMPERATURE)
    mqtt.subscribe(client, MQTT_TOPIC_ALARM)
    mqtt.subscribe(client, MQTT_TOPIC_TEMPERATURE_SETPOINT)

    while True:
        client.check_msg()

        buzzer.update()
        update_lamp()
        heater.update()

        if (ticks_diff(ticks_ms(), mqtt_upload_prev_time) >= mqtt_period_ms) or shared['mqtt_topic_update_flag'] == True:
            mqtt_upload_prev_time = ticks_ms()
            shared['mqtt_topic_update_flag'] = False
            client.publish(MQTT_TOPIC_HEATER, b'ON' if heater.state else b'OFF')

        if ticks_diff(ticks_ms(), terminal_print_prev_time) >= terminal_print_period_ms:
            terminal_print_prev_time = ticks_ms()
            print_info()
        
except Exception as e:
    my_print('Error:', e)

finally:
    led.value(0)

    buzzer.state = False
    buzzer.update()

    heater.pin.value(0)

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