import network
import time
import dht
import machine
import json
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
def connect_mqtt():
    global mqtt_client
    try:
        mqtt_client = MQTTClient("ESP32", UBIDOTS_BROKER, UBIDOTS_PORT, user=UBIDOTS_TOKEN, password=UBIDOTS_TOKEN)
        mqtt_client.connect()
        print("✅ Connected to Ubidots MQTT!")
    except Exception as e:
        print("❌ Failed to connect to Ubidots MQTT:", e)

connect_mqtt()  # First connection

# ✅ Initialize Sensors (DHT11 & Button)
dht_pin = machine.Pin(4)
sensor = dht.DHT11(dht_pin)

button_pin = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)  # Button on GPIO21

while True:
    try:
        # ✅ DHT11 Read (Prevent Timeout)
        time.sleep(2)  # Delay sebelum membaca sensor DHT
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        # ✅ Read Button State
        button_state = button_pin.value()  # 1 = Tidak Ditekan, 0 = Ditekan

        # ✅ JSON Data
        data = {
            "sensor_id": "esp32",
            "temperature": temp,
            "humidity": hum,
            "button": button_state  # Tambahkan status tombol
        }
        json_data = json.dumps(data)  # Convert dictionary to JSON string
        ubi_data = '{"temperature": ' + str(temp) + ', "humidity": ' + str(hum) + ', "button": ' + str(button_state) + '}'

        # ✅ Send Data to Ubidots via MQTT
        try:
            mqtt_client.publish(MQTT_TOPIC, ubi_data)
            print("📡 Sent to Ubidots:", ubi_data)
        except Exception as e:
            print("❌ MQTT Error:", e)
            connect_mqtt()  # Reconnect jika MQTT gagal

        # ✅ Send Data to Flask Server
        try:
            response = urequests.post(FLASK_SERVER, json=data, headers={"Content-Type": "application/json"})
            print("🌍 Sent to Flask:", response.text)
            response.close()  # Close connection
        except Exception as e:
            print("❌ Flask Server Error:", e)

    except Exception as e:
        print("❌ Sensor Error:", e)

    time.sleep(5)