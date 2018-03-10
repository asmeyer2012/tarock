import Pyro4
from gameplay.player import *
from gameplay.cards import *
import time

"""
Hold up, need to start the greeting server first.
Directions are in greeting-server.py

Once that's done, this process can communicate with it.
"""

nameserver = Pyro4.locateNS()
tarockuri = nameserver.lookup("example.tarock")

tarock = Pyro4.Proxy(tarockuri)

name = raw_input("What is your name? ").strip()
idx = tarock.newplayer(name)
print "You have been registered as " + tarock.printplayer(idx)
if idx > 0:
  mess = "Other players are:\n"
  for p in range (idx):
    mess += tarock.printplayer(p)
  print mess
else:
  print "No other players\n"

if idx == 3:
  tarock.deal()
else:
  tarock.ready()

print "Here is a hand of cards:\n"
print(tarock.printHand(idx))

time.sleep(10)
tarock.leavetable(idx)
