import paho.mqtt.client as mqtt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json

# Store received data
data = []

# Define callbacks with VERSION2 signature
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor/data")

def on_message(client, userdata, msg, properties=None):
    try:
        payload = msg.payload.decode("utf-8")
        json_data = json.loads(payload)
        
        current_time = datetime.now()
        data.append((current_time, json_data["temperature"], json_data["humidity"]))
        
        # Keep last 100 points
        if len(data) > 100:
            data.pop(0)
            
        # Create DataFrame
        df = pd.DataFrame(data, columns=["timestamp", "temperature", "humidity"])
        
        # Update plot
        plt.clf()
        plt.plot(df["timestamp"], df["temperature"], 'r-', label="Temperature (°C)")
        plt.plot(df["timestamp"], df["humidity"], 'b-', label="Humidity (%)")
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Real-time Sensor Data')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.gcf().autofmt_xdate()
        
        plt.draw()
        plt.pause(0.1)
    except Exception as e:
        print(f"Error processing message: {e}")

def start_visualization(broker="localhost", port=1883):
    # Create client with VERSION2 API
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to MQTT broker
    client.connect(broker, port)

    # Setup visualization
    plt.ion()
    plt.figure(figsize=(10, 6))

    # Start client loop
    client.loop_start()

    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        print("Shutting down visualization...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    start_visualization()
