import os
import argparse
from dotenv import load_dotenv
import serial
from pynitel import pynitel
import threading
import time
from twitter import Twitter, OAuth, oauth_dance

class Twittinitel:
    def __init__(self, port, baudrate=1200):
        self.minitel = pynitel.Pynitel(serial.Serial(port, baudrate,
                                                parity=serial.PARITY_EVEN, bytesize=7,
                                                timeout=2))
        self.buffers = {
            "messages": [],
            "send": ""
        }

        self.minitel.cls()
        self.redraw()

    def redraw(self):
        self.minitel.cls()
        self.minitel.cursor(False)
        self.minitel.pos(0, 0)
        self.minitel._print("3615 Twitter\n\r\n\r")
        for message in self.buffers["messages"][-5:]:
            self.minitel._print("{}: {}\n\r".format(message.get("user").get("screen_name"), message.get("text")))

        self.minitel._print("\n> " + self.buffers["send"])

    def handle_message(self, messages):
        if self.buffers["messages"] != messages:
            self.buffers["messages"] = messages
            self.redraw()

    def read_keys(self, twitter):
        while True:
            key = self.minitel.conn.read(1).decode()
            new_buffer = self.buffers.get("send")
            if key == '\x13':  # SEP donc touche Minitel...
                key = self.minitel.conn.read(1).decode()
                if key == '\x41':  # Touche Envoi
                    self.buffers["send"] = ""
                    twitter.statuses.update(status=new_buffer)
                    time.sleep(0.5)
                    self.redraw()
                if key == '\x47':  # Touche Effacement
                    self.buffers["send"] = self.buffers["send"][:-1]
                    self.redraw()
                else:
                    print("Touche Minitel non reconnue: {}".format(hex(ord(key))))
            else:
                new_buffer += key
                if new_buffer != self.buffers.get("send"):
                    self.buffers.update({"send": new_buffer})

def update_timeline(twitter, minitel):
    while True:
        messages = twitter.statuses.home_timeline(count=200)
        ok_messages = []
        for message in messages:
            if "RT @" not in message.get("text") and "t.co/" not in message.get("text") and not message.get("extended_entities"):
                ok_messages.append(message)
        minitel.handle_message(ok_messages)
        time.sleep(30)

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description='Twittinitel')
    parser.add_argument('serial_port', type=str, help='Serial port')
    parser.add_argument('--baudrate', type=int, help='Serial baudrate', default=1200)
    args = parser.parse_args()

    twitter = Twitter(auth=OAuth(os.environ.get("OAUTH_KEY"), os.environ.get("OAUTH_SECRET"), os.environ.get("CONSUMER_KEY"), os.environ.get("CONSUMER_SECRET")))

    minitel = Twittinitel(args.serial_port, baudrate=args.baudrate)

    p = threading.Thread(target=update_timeline, args=(twitter, minitel, ))
    p.start()

    minitel.read_keys(twitter)
