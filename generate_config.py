from pathlib import Path

CONFIG_TEMPLATE = """wifi_ssid = ''
wifi_password = ''
mqtt_server = b''
mqtt_username = None
mqtt_password = None
"""

# Create generic directory if it doesn't exist
Path("generic").mkdir(exist_ok=True)

# Generate config.py template
with open("generic/config.py", "w", encoding="utf-8") as f:
    f.write(CONFIG_TEMPLATE)

print("Generated: ./generic/config.py")