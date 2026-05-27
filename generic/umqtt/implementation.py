from generic.umqtt.simple import MQTTClient
import generic.config as config

# MQTT Parameters
MQTT_SERVER = config.mqtt_server
MQTT_PORT = 1883
MQTT_USER = config.mqtt_username
MQTT_PASSWORD = config.mqtt_password
MQTT_KEEPALIVE = 7200
MQTT_SSL = False   # set to False if using local Mosquitto MQTT broker
MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}

# Constants for MQTT Topics
MQTT_TOPIC_LAMP = 'home_iot/lamp'
MQTT_TOPIC_TEMPERATURE = 'home_iot/temperature'
MQTT_TOPIC_TEMPERATURE_SETPOINT = 'home_iot/temperature_setpoint'
MQTT_TOPIC_HEATER = 'home_iot/heater'
MQTT_TOPIC_ALARM = 'home_iot/alarm'

def connect_mqtt(client_id):
    try:
        client = MQTTClient(client_id=client_id,
                            server=MQTT_SERVER,
                            port=MQTT_PORT,
                            user=MQTT_USER,
                            password=MQTT_PASSWORD,
                            keepalive=MQTT_KEEPALIVE,
                            ssl=MQTT_SSL,
                            ssl_params=MQTT_SSL_PARAMS)
        client.connect()
        return client
    except Exception as e:
        print('Error connecting to MQTT:', e)
        return None

# Subcribe to MQTT topics
def subscribe(client, topic):
    client.subscribe(topic)
    print('Subscribe to topic:', topic)