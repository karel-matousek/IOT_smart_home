from machine import Pin
from time import sleep
from generic.wifi import initialize_wifi
from generic import config
from generic.umqtt import implementation as mqtt
from generic.my_print import my_print

led = Pin("LED", Pin.OUT)

# Constants for MQTT Topics
MQTT_TOPIC_LAMP = 'home_iot/lamp'
MQTT_TOPIC_TEMPERATURE = 'home_iot/temperature'
MQTT_TOPIC_HEATER = 'home_iot/heater'

MQTT_CLIENT_ID = b"actuator_picow"

# Callback function that runs when you receive a message on subscribed topic
def mqtt_received_callback(topic, message):
    # Perform desired actions based on the subscribed topic and response
    my_print(f"Received message on topic: {topic}")
    my_print(f"Response: {message}")
    # Check the content of the received message
    if message == b'ON':
        my_print('Turning LED ON')
        led.value(1)  # Turn LED ON
    elif message == b'OFF':
        my_print('Turning LED OFF')
        led.value(0)  # Turn LED OFF
    else:
        my_print('Unknown command')

try:
    if not initialize_wifi(config.wifi_ssid, config.wifi_password):
        my_print('Error connecting to the network... exiting program')
    else:
        # Connect to MQTT broker, start MQTT client
        client = mqtt.connect_mqtt(MQTT_CLIENT_ID)
        my_print('Connected to MQTT broker successfully!')

        client.set_callback(mqtt_received_callback)
        mqtt.subscribe(client, MQTT_TOPIC_LAMP)
        mqtt.subscribe(client, MQTT_TOPIC_TEMPERATURE)
        while True:
            client.check_msg()



            #client.publish('mode_iot/secret', 'send dudes')
            sleep(1)  # Keep the program running to maintain MQTT connection

except Exception as e:
    my_print('Error:', e)