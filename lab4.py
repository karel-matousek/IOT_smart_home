import machine
import time
import aht20
from wifi import initialize_wifi
import config
import implementation as mqtt
from my_print import my_print

DEVICE_ADDR = 56
period = 3000

# Buttons
gpio20 = machine.Pin(20, machine.Pin.IN)
gpio21 = machine.Pin(21, machine.Pin.IN)

# ADHT20
i2c_handle = machine.I2C(0, scl = 1, sda = 0, freq = 100000)
#print(i2c_handle.scan())

sensor = aht20.TMPSensor(i2c_handle, DEVICE_ADDR)
sensor.measure()

# Constants for MQTT Topics
MQTT_TOPIC_LAMP = 'home_iot/lamp'
MQTT_TOPIC_TEMPERATURE = 'home_iot/temperature'
MQTT_TOPIC_HUMIDITY = 'home_iot/humidity'
MQTT_TOPIC_ALARM = 'home_iot/alarm'

MQTT_CLIENT_ID = b"sensors_picow"

try:
    if not initialize_wifi(config.wifi_ssid, config.wifi_password):
        my_print('Error connecting to the network... exiting program')
    else:
        # Connect to MQTT broker, start MQTT client
        client = mqtt.connect_mqtt(MQTT_CLIENT_ID)
        my_print('Connected to MQTT broker successfully!')

        #client.set_callback(mqtt_received_callback)
        #mqtt.subscribe(client, MQTT_TOPIC_LAMP)
        #mqtt.subscribe(client, MQTT_TOPIC_TEMPERATURE)
        while True:
            client.check_msg()
            #client.publish('mode_iot/secret', 'send dudes')
            
            sensor.measure()
            client.publish(MQTT_TOPIC_TEMPERATURE, str(sensor.temp))
            client.publish(MQTT_TOPIC_HUMIDITY, str(sensor.hum))
            #print(sensor.hum)
            #print(sensor.temp)
            
            if gpio20.value():
                client.publish(MQTT_TOPIC_LAMP, "OFF")
            else:
                client.publish(MQTT_TOPIC_LAMP, "ON")
                
                
            if gpio21.value():
                client.publish(MQTT_TOPIC_ALARM, "OFF")
            else:
                client.publish(MQTT_TOPIC_ALARM, "ON")
                
            
            time.sleep_ms(1000)

except Exception as e:
    my_print('Error:', e)