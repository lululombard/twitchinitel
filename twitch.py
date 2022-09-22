#!/usr/bin/env python3

from curses.ascii import isupper
import serial
import pynitel
import threading
import time
from twitch_chat_irc import twitch_chat_irc

message_from = "lululombard"
channel_name = "KabameTheWolf"

class MinitelTwitch:
    def __init__(self):
        self.minitel = pynitel.Pynitel(serial.Serial('/dev/tty.usbserial-AB0OZ3VO', 1200,
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
        self.minitel._print("Twitchinitel - " + channel_name + "\n\r\n\r")
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
                    twitch.send(channel_name, new_buffer)
                    self.buffers["messages"].append({
                        "display-name": message_from,
                        "message": new_buffer
                    })
                    self.redraw()
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
                    # self.redraw()

def read_chat(twitch, minitel):
    twitch.listen(channel_name, on_message=minitel.handle_message)

if __name__ == "__main__":

    minitel_twitch = MinitelTwitch()

    twitch = twitch_chat_irc.TwitchChatIRC()

    p = threading.Thread(target=read_chat, args=(twitch, minitel_twitch, ))
    p.start()

    minitel_twitch.read_keys(twitch)
