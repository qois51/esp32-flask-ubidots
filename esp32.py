import network
import time
import dht
import machine
import urequests  # For HTTP requests
from umqtt.simple import MQTTClient

# ✅ WiFi Configuration
SSID = "GP_C3"
PASSWORD = "gajahlampung"

# ✅ MQTT Ubidots Configuration
UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_PORT = 1883
UBIDOTS_TOKEN = "BBUS-puiqyc43oc0ISKTwO9OVwL0yWjSWVf"
MQTT_TOPIC = "/v1.6/devices/esp32"

# ✅ Flask Server Configuration (Use your laptop's IP)
FLASK_SERVER = "http://192.168.1.220:3000/push"

# ✅ Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
time.sleep(1)

while not wifi.isconnected():
    time.sleep(1)

print("✅ Connected to WiFi! IP:", wifi.ifconfig()[0])

# ✅ Initialize MQTT Client
mqtt_client = MQTTClient("ESP32", UBIDOTS_BROKER, UBIDOTS_PORT, user=UBIDOTS_TOKEN, password=UBIDOTS_TOKEN)

try:
    mqtt_client.connect()
    print("✅ Connected to Ubidots MQTT!")
except Exception as e:
    print("❌ Failed to connect to Ubidots!", e)

# ✅ Initialize Sensors (DHT11 & LDR)
dht_pin = machine.Pin(4)
sensor = dht.DHT11(dht_pin)
ldr_pin = machine.ADC(machine.Pin(34))  # GPIO34 for LDR
ldr_pin.atten(machine.ADC.ATTN_11DB)  # 0 - 3.3V range

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        ldr_value = ldr_pin.read()  # Read ADC (0-4095)

        # ✅ JSON Data
        data = {
            "sensor_id": "esp32",
            "temperature": temp,
            "humidity": hum,
            "ldr": ldr_value
        }
        json_data = '{"temperature": ' + str(temp) + ', "humidity": ' + str(hum) + ', "ldr": ' + str(ldr_value) + '}'

        # ✅ Send data to Ubidots via MQTT
        mqtt_client.publish(MQTT_TOPIC, json_data)
        print("📡 Sent to Ubidots:", json_data)

        # ✅ Send data to Flask server via HTTP
        response = urequests.post(FLASK_SERVER, json=data, headers={"Content-Type": "application/json"})
        print("🌍 Sent to Flask:", response.text)

    except Exception as e:
        print("❌ Sensor or Network Error:", e)

    time.sleep(5)