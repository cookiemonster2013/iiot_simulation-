from asyncua import ua, Server
import asyncio
import random
import paho.mqtt.client as mqtt
import json

class OpcUaMqttBridge:
    def __init__(self, opcua_endpoint="opc.tcp://0.0.0.0:4840/freeopcua/server/", 
                mqtt_broker="localhost", mqtt_port=1883, mqtt_topic="sensor/data"):
        self.opcua_endpoint = opcua_endpoint
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.server = None
        self.mqtt_client = None
        
    async def setup_opcua_server(self):
        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(self.opcua_endpoint)
        
        # Register namespace
        uri = "http://examples.freeopcua.github.io"
        idx = await self.server.register_namespace(uri)
        
        # Get Objects node
        objects = await self.server.get_objects_node()
        
        # Create sensor object
        myobj = await objects.add_object(idx, "SensorNode")
        temperature = await myobj.add_variable(idx, "Temperature", 0.0)
        humidity = await myobj.add_variable(idx, "Humidity", 0.0)
        
        # Set variables to be writable
        await temperature.set_writable(True)
        await humidity.set_writable(True)
        
        return idx, temperature, humidity
        
    def setup_mqtt_client(self):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        self.mqtt_client.loop_start()
        
    async def run(self):
        # Setup OPC UA server
        idx, temperature, humidity = await self.setup_opcua_server()
        
        # Setup MQTT client
        self.setup_mqtt_client()
        
        async with self.server:
            try:
                while True:
                    # Generate random values
                    temp_value = random.uniform(20.0, 25.0)
                    hum_value = random.uniform(30.0, 50.0)
                    
                    # Update OPC UA variables
                    await temperature.write_value(temp_value)
                    await humidity.write_value(hum_value)
                    
                    # Publish to MQTT
                    payload = json.dumps({
                        "temperature": round(temp_value, 2),
                        "humidity": round(hum_value, 2)
                    })
                    self.mqtt_client.publish(self.mqtt_topic, payload)
                    
                    print(f"Published - Temperature: {temp_value:.2f}, Humidity: {hum_value:.2f}")
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()

async def main():
    bridge = OpcUaMqttBridge()
    await bridge.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bridge stopped by user")
