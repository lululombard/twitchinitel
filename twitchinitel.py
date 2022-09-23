import os
import argparse
from dotenv import load_dotenv
import serial
from pynitel import pynitel
import threading
import time
from twitch_chat_irc import twitch_chat_irc

class Twitchinitel:
    def __init__(self, channel_name, port, baudrate=1200):
        load_dotenv()
        self.minitel = pynitel.Pynitel(serial.Serial(port, baudrate,
                                                parity=serial.PARITY_EVEN, bytesize=7,
                                                timeout=2))
        self.buffers = {
            "messages": [],
            "send": ""
        }

        self.channel_name = channel_name

        self.minitel.cls()
        self.redraw()

    def redraw(self):
        self.minitel.cls()
        self.minitel.cursor(False)
        self.minitel.pos(0, 0)
        self.minitel._print("Twitchinitel - " + self.channel_name + "\n\r\n\r")
        for message in self.buffers["messages"][-7:]:
            self.minitel._print("{display-name}: {message}\n\r".format(**message))

        self.minitel._print("\n> " + self.buffers["send"])

    def handle_message(self, message):
        self.buffers["messages"].append(message)
        self.redraw()

    def read_keys(self, twitch):
        while True:
            key = self.minitel.conn.read(1).decode()
            new_buffer = self.buffers.get("send")
            if key == '\x13':  # SEP donc touche Minitel...
                key = self.minitel.conn.read(1).decode()
                if key == '\x41':  # Touche Envoi
                    self.buffers["send"] = ""
                    twitch.send(self.channel_name, new_buffer)
                    self.buffers["messages"].append({
                        "display-name": os.environ.get("NICK"),
                        "message": new_buffer
                    })
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

def read_chat(twitch, channel_name, minitel):
    twitch.listen(channel_name, on_message=minitel.handle_message)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Twitchinitel')
    parser.add_argument('serial_port', type=str, help='Serial port')
    parser.add_argument('channel_name', type=str, help='Channel name')
    parser.add_argument('--baudrate', type=int, help='Serial baudrate', default=1200)
    args = parser.parse_args()

    minitel = Twitchinitel(args.channel_name, args.serial_port, baudrate=args.baudrate)

    twitch = twitch_chat_irc.TwitchChatIRC()

    p = threading.Thread(target=read_chat, args=(twitch, args.channel_name, minitel, ))
    p.start()

    minitel.read_keys(twitch)
