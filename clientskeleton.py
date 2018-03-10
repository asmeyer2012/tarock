import Pyro4
from gameplay.player import *
from gameplay.cards import *

"""
Hold up, need to start the greeting server first.
Directions are in greeting-server.py

Once that's done, this process can communicate with it.
"""

nameserver = Pyro4.locateNS()
tarockuri = nameserver.lookup("example.tarock")

tarockhandle = Pyro4.Proxy(tarockuri)

name = raw_input("What is your name? ").strip()
idx = tarockhandle.newplayer(name)
print "You have been registered as " + tarockhandle.printplayer(idx)

tarockhandle.deal()

print "Here is a hand of cards:\n"
print(tarockhandle.printHand(0))
