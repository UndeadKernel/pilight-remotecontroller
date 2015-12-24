#!/usr/bin/env python

import sys
import os
import socket
import json
import subprocess
from threading import Timer
from daemon import Daemon
from button import Button

pilight_daemon = ("10.0.1.3", 5000)
devnull = open(os.devnull, "w")

class RemoteController(Daemon):
    def run(self):
        # Init the buttons
        self.configButtons()

        # Connect to the Pilight daemon
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0)
        self.s.connect(pilight_daemon)
        # Identifiy with the daemon
        self.s.send('{"action":"identify","options":{"receiver":1}}\n')

        # Wait for a status response from the daemon and start on 'success'
        text = "";
        while True:
            line = self.s.recv(1024)
            text += line;
            if "\n\n" in line[-2:]:
                text = text[:-2];
                break;

        # Stop if we were not able to connect to pilight
        if text != '{"status":"success"}':
            sys.exit(1)

        text = "";
        while True:
            line = self.s.recv(1024)
            text += line;
            if "\n\n" in line[-2:]:
                text = text[:-2];
                for f in iter(text.splitlines()):
                    self.execLine(f);
                text = "";
        s.close()

    def configButtons(self):
        self.buttons = []
        self.buttons.append(Button('play', 7, 2, u'on', 2))
        self.buttons.append(Button('stop', 7, 2, u'off', 2))
        self.buttons.append(Button('next', 7, 4, u'on', 2))
        self.buttons.append(Button('prev', 7, 4, u'off', 2))
        self.buttons.append(Button('sleep', 7, 2, u'on', 8))

    def playSound(self):
        subprocess.Popen(['/usr/bin/mpg123', '/home/mpd/scripts/beep.mp3'], stdout=devnull, stderr=devnull);
        print 'Play beep'

    def execLine(self, line):
        try:
            obj = json.loads(line)
        except ValueError, e:
            return

        button = self.matchButton(obj)

        if button == 'play':
            # Play music
            subprocess.call(['/usr/bin/mpc', 'play'], stdout=devnull, stderr=devnull);
            self.playSound();
        elif button == 'stop':
            # Stop music
            subprocess.call(['/usr/bin/mpc', 'stop'], stdout=devnull, stderr=devnull);
            self.playSound();
        elif button == 'next':
            # Skip track
            subprocess.call(['/usr/bin/mpc', 'next'], stdout=devnull, stderr=devnull);
        elif button == 'prev':
            # Previous track
            subprocess.call(['/usr/bin/mpc', 'prev'], stdout=devnull, stderr=devnull);
        elif button == 'sleep':
            # Set a sleep timer of 45 minutes
            t = Timer(2700, self.goToSleep)
            t.start()
            self.playSound();
            print 'Sleep.'

    def matchButton(self, obj):
        for button in self.buttons:
            match = button.match(obj)
            if match != '':
                return match

    def goToSleep(self):
        self.s.send('{"action":"control","code":{"device":"PiMoteA","state":"off"}}\n')


if __name__ == "__main__":
    daemon = RemoteController('/home/mpd/remotecontroller.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
            subprocess.call(['/usr/bin/mpc', 'stop'], stdout=devnull, stderr=devnull);
        elif 'run':
            daemon.run()
