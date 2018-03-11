# KLabe attempt at a Python class for tracking the game
import Pyro4
import sys
sys.path.insert(0, '../')
from gameplay.deck_slovenian import *
from gameplay.cards import *
from gameplay.player import *
import time

"""
!! start the naming server first with:
python -m Pyro4.naming
   or
pyro4-ns

!! it is possible to query the naming server with:
$ python -m Pyro4.nsc list

!! once the naming server is running, start this process in the background with:
$ python serverskeleton.py
"""

@Pyro4.expose
class TarockGame:
  def __init__(self):
    self.players = list()
    self.dealer = 0

  def getplayers(self):
    return len(self.players)

  def newplayer(self, name):
    player = Player(name)
    self.players.append(player)
    return len(self.players) - 1

  def leavetable(self, idx):
    del self.players[idx]

  def ready(self):
    while len(self.players) < 4:
      time.sleep(1)

  def deal(self):
    deck = slovenianDeck()
    pile = Pile()
    pile.addCards( deck.getShuffled() )
    for x in range(12):
      for p in range(4):
        c1 = pile.takeCard()
        self.players[p].hand.putCard(c1)

  def printplayer(self, idx):
    return self.players[idx].name

  def handlen(self, idx):
    return self.players[idx].hand.pilelen()

  def printCard(self, idx, i):
    pile = self.players[idx].hand
    pile.orderPile()
    return pile.printCard(i)

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

tarock = TarockGame()
uri = daemon.register(tarock)
ns.register("example.tarock", uri)

print("Ready.")
daemon.requestLoop()
