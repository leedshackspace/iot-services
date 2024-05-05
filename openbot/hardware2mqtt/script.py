"""
messageOpenSpace = [
  ("The space is open to members! Someone will be here for about ", "an hour", "!"),
  ("The space will be open (to members) for approximately ", "1 hour", "."),
  ("Got something to make? There's someone in the space for the next ", "hour or so", "."),
  ("Hackspace! Open to members! For approximately ", "an hour", "!"),
  ("Leeds Hackspace is open to members for around ", "an hour", "."),
  ("Get yourself down to the space and build things! Leeds Hackspace is open for ", "an hour", "."),
  ("Leeds Hackspace Members! There's someone at the space for at least the next ", "hour", ".")
];

messageCloseSpace=[
  "The space is closed.",
  "The space is closed. You can get in if you're a keyholder.",
  "Leeds Hackspace is currently empty.",
  "There's apparently nobody here. The hackspace is closed.",
  "The space is empty.",
  "The hackspace is empty."
];
"""

messageOpenSpace = [
  ("OpenBot -The space is open to members! Someone will be here for about ", "an hour", "!"),
  ("OpenBot says the space will be open (to members) for approximately ", "1 hour", "."),
  ("OpenBot - Are you a member with something to make? There's someone in the space for the next ", "hour or so", "."),
  ("OpenBot - Hackspace! Open to members! For approximately ", "an hour", "!"),
  ("OpenBot - Leeds Hackspace is open to members for around ", "an hour", "."),
  ("Members get yourself down to the space and build things! OpenBot says Leeds Hackspace is open for ", "an hour", "."),
  ("Leeds Hackspace Members! OpenBot says there's someone at the space for at least the next ", "hour", ".")
];

messageCloseSpace=[
  "The space is closed.",
  "The space is closed. You can get in if you're a keyholder.",
  "Leeds Hackspace is currently empty.",
  "There's apparently nobody here. The hackspace is closed.",
  "The space is empty.",
  "The hackspace is empty."
];

from contextlib import closing
import paho.mqtt.client as mqtt
import configparser # TODO Add config
import math, sched, time, random, datetime

config = configparser.ConfigParser()

config.read('config.ini')

server = config["mqtt"].get("server", "127.0.0.1")
port = int(config["mqtt"].get("port", "1883"))
keep_alive = int(config["mqtt"].get("keep_alive", "60"))

client = mqtt.Client()

lastDial = 0;

def ceil_dt(dt, delta):
    return dt + (datetime.datetime.min - dt) % delta


def handleButton():
    hours = math.floor((lastDial-64) / 128);
    hours = max(hours, 0);
    open = (hours != 0)
    closing = time.mktime(ceil_dt((datetime.datetime.now() + datetime.timedelta(hours=hours)),
        datetime.timedelta(minutes=15)).timetuple())
    msg = ""
    if (open) :
        msgTemplate = random.sample(messageOpenSpace, 1)[0];
        msg = msgTemplate[0] + (msgTemplate[1] if (hours == 1) else str(hours) + " hours") + msgTemplate[2] + " (" + datetime.datetime.fromtimestamp(closing).strftime('%H:%M') + ")"
    else:
        msg = random.sample(messageCloseSpace, 1)[0];
    client.publish("openbot/open", str(open))
    #client.publish("openbot/open", str(open))
    client.publish("openbot/message", str(msg))
    client.publish("openbot/hours", str(hours))
    client.publish("openbot/closing", str(closing))
    #client.publish("openbot/message", str(msg))

def toggleLight(state):
    #if (state == "ON"):
    client.publish("esphome/openbot/prime-test/switch/red_led/command", state)
    #else:
    #    client.publish("esphome/openbot/prime-test/switch/red_led/state", false)

def on_message(client, userdata, message):
    if (message.topic == "esphome/openbot/prime-test/binary_sensor/button/state"):
        toggleLight(message.payload.decode())
        if (message.payload.decode() == "ON"):
            handleButton();
        return
    if (message.topic == "esphome/openbot/prime-test/sensor/knob_pos/state"):
        global lastDial
        lastDial = float(message.payload.decode())
        #print(lastDial)
        return

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("esphome/openbot/prime-test/binary_sensor/button/state")
    client.subscribe("esphome/openbot/prime-test/sensor/knob_pos/state")

client.on_connect = on_connect
client.on_message = on_message

client.connect(server, port, keep_alive)
print("OpenBot Hardwar2MQTT Starting...")
client.loop_forever()