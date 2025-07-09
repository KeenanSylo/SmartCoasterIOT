from mqtt import MQTTClient
from lib import keys  # Correct import


class AdafruitIO:
    def __init__(self):
        self.client = None
        self.connected = False

    def connect(self):
        #Connect to Adafruit IO
        try:
            self.client = MQTTClient(
                client_id="smartCoaster" + keys.AIO_USER,
                server=keys.AIO_SERVER,
                user=keys.AIO_USER,
                password=keys.AIO_KEY,
                port=keys.AIO_PORT
            )
            self.client.connect()
            self.connected = True
            print("Connected to Adafruit IO")
            return True
        except Exception as e:
            print("Adafruit IO connection failed:", e)
            self.connected = False
            return False

    def publish(self, feed_key, value):
        #Publish to a specific feed
        if not self.connected:
            if not self.connect():
                return False
        try:
            topic = f"{keys.AIO_USER}/feeds/{feed_key}"
            self.client.publish(topic, str(value))
            print(f"Published to {feed_key}: {value}")
            return True
        except Exception as e:
            print("Publish failed:", e)
            self.connected = False
            return False
