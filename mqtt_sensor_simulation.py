import time
import random
import json
import paho.mqtt.client as mqtt

def simulate_sensor_data(broker="localhost", port=1883, topic="sensor/data", interval=1.0):
    # Create client with latest API version
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(broker, port)
    
    try:
        while True:
            # Generate random sensor data
            temperature = random.uniform(20.0, 25.0)
            humidity = random.uniform(30.0, 50.0)
            
            # Create payload
            payload = json.dumps({
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "timestamp": time.time()
            })
            
            # Publish to MQTT topic
            client.publish(topic, payload)
            print(f"Published - Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%")
            
            # Wait before next reading
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping simulation...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    simulate_sensor_data()
