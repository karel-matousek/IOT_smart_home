import sys
sys.path.append("/")
from machine import Pin
from time import ticks_ms, ticks_diff
from generic import config
from generic.wifi import initialize_wifi
from generic.umqtt import implementation as mqtt
from generic.umqtt.implementation import MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_TEMPERATURE_SETPOINT, MQTT_TOPIC_HEATER
from generic.my_print import my_print
from generic.heater import Heater

# === Objects
wlan = None
client = None
heater = Heater()

# === Timing variables
mqtt_period_ms = 30000
mqtt_upload_prev_time = 0
#
terminal_print_period_ms = 1000
terminal_print_prev_time = 0

# === Constants
MQTT_CLIENT_ID = b"gateway_picow"

def mqtt_received_callback(topic, message):
    topic = topic.decode('utf-8')
    message = message.decode('utf-8')

    my_print(f"Received message on topic: {topic}, response: {message}")

    if topic == MQTT_TOPIC_TEMPERATURE:
        try:
            new_temperature = float(message)
            heater.current_temperature_dC = new_temperature
            my_print(f'Updated current temperature to {new_temperature:.2f} °C')
        except ValueError:
            my_print('Invalid temperature value received')

    else:
        my_print('Unknown topic received')

def print_info():
    my_print("=================================================================")
    print(f"\tTemperature: {heater.current_temperature_dC:.2f} °C")
    print(f"\tHeater: \tstate: {'ON' if heater.state else 'OFF'} \tsetpoint: {heater.setpoint_dC:.2f} °C \thysteresis: {heater.hysteresis_dC:.2f} °C")

try:
    print("=== Gateway =============================================================")

    wlan = initialize_wifi(config.wifi_ssid, config.wifi_password)
    if not wlan:
        raise Exception('WiFi connection failed')
    my_print('Connected to WiFi successfully!')
    
    client = mqtt.connect_mqtt(MQTT_CLIENT_ID)
    if not client:
        raise Exception('MQTT connection failed')
    my_print('Connected to MQTT broker successfully!')

    client.set_callback(mqtt_received_callback)
    mqtt.subscribe(client, MQTT_TOPIC_TEMPERATURE)

    while True:
        client.check_msg()

        heater.change_setpoint()
        heater.calculate_state()

        if heater.state_update_flag == True or ticks_diff(ticks_ms(), heater.state_last_upload_time) >= mqtt_period_ms:
            heater.state_update_flag = False
            heater.state_last_upload_time = ticks_ms()
            client.publish(MQTT_TOPIC_HEATER, b'ON' if heater.state else b'OFF')
        if heater.setpoint_update_flag == True or ticks_diff(ticks_ms(), heater.setpoint_last_upload_time) >= mqtt_period_ms:
            heater.setpoint_update_flag = False
            heater.setpoint_last_upload_time = ticks_ms()
            client.publish(MQTT_TOPIC_TEMPERATURE_SETPOINT, f"{heater.setpoint_dC:.2f}".encode('utf-8'))

        if ticks_diff(ticks_ms(), terminal_print_prev_time) >= terminal_print_period_ms:
            terminal_print_prev_time = ticks_ms()
            print_info()
        
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