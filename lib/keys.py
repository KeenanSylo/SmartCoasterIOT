import ubinascii              # Conversions between binary data and various encodings
import machine                # To Generate a unique id from processor

# Wireless network
WIFI_SSID =  "Pintu12"
WIFI_PASS = "55900560"

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "KeenanSylo"
AIO_KEY = "aio_qzuL48UKdLmCykBidvPdmp6DBcpI"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_COASTER_FEED = "KeenanSylo/feeds/oncoaster"
AIO_TEMP_FEED = "KeenanSylo/feeds/temp"