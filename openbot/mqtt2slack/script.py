import paho.mqtt.client as mqtt
import configparser
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

config = configparser.ConfigParser()

config.read('config.ini')

# MQTT config
server = config["mqtt"].get("server", "127.0.0.1")
port = int(config["mqtt"].get("port", "1883"))
keep_alive = int(config["mqtt"].get("keep_alive", "60"))

# Openbot Config
root_endpoint = config["openbot"].get("endpoint", "openbot")

# Slack config
slack_key = config["slack"].get("api_key", "example")
slack_channel = config["slack"].get("channel", "general")

client = mqtt.Client()
slack_client = WebClient(token=slack_key)

lastMessage = ""

def on_message(client, userdata, message):
    if (message.topic == root_endpoint+"/message"):
        print(message.payload.decode())
        try:
            response = slack_client.chat_postMessage(
                channel=slack_channel,
                text=message.payload.decode()
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(root_endpoint+"/message")
    client.subscribe(root_endpoint+"/tweet")

client.on_connect = on_connect
client.on_message = on_message

client.connect(server, port, keep_alive)

client.loop_forever()