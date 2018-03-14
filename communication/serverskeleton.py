# KLabe attempt at a Python class for tracking the game
import Pyro4
import sys
sys.path.insert(0, '../')
from gameplay.deck_slovenian import *
from gameplay.cards import *
from gameplay.player import *
from gameplay.orderofplay import *
from gameplay.auction import *
from intertools import cycle
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
    self.stage = Stage.INITIATE
    self.players = list()
    self.dealeridx = 0
    self.table = list()
    self.tablec = None
    self.auction = None
    self.compulsoryklop = False

  def newplayer(self, name):
    player = Player(name)
    curi = ns.lookup("example.client.{0}".format(name))
    player.client = Pyro4.Proxy(curi)
    self.players.append(player)
    if len(self.players) <= 4:
      self.table.append(player)
    if len(self.players) == 4 and self.stage == Stage.INITIATE:
      self.tablec = cycle(table)
      self.stage = Stage.DEAL
      broadcast("Ready for {0} to deal".format(self.players[self.dealer].name))
    return len(self.players) - 1

  def leavetable(self, idx):
    broadcast("{0} is leaveing.".format(self.players[idx].name))
    del self.players[idx]
    for p in self.players:
      p.client.updateidx(idx)

  def printplayer(self, idx):
    return self.players[idx].name

  def handlen(self, idx):
    return self.players[idx].hand.pilelen()

  def printCard(self, idx, i):
    pile = self.players[idx].hand
    pile.orderPile()
    return pile.printCard(i)

  def broadcast(self, mess):
    for p in self.players:
      p.client.writegame(mess)

  def broadcastmsg(self, name, mess):
    for p in self.players:
      p.client.writemsg(name,mess)

  def deal(self, idx):
    if self.stage == Stage.DEAL and idx == self.dealer:
      deck = slovenianDeck()
      pile = Pile()
      pile.addCards( deck.getShuffled() )
      for x in range(12):
        for p in range(4):
          c1 = pile.takeCard()
          self.players[p].hand.putCard(c1)
      self.stage = Stage.BID
      broadcast("Hand dealt!")
      self.auction = Auction(self.player[idx], self.tablec, self.compulsoryklop)
      self.auction.Start(idx)
      broadcast("{0} has the first bid at Two".format(self.players[self.auction.livebidder].name))
    else:
      self.player[idx].client.writegame("Cannot deal from this state")

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

tarock = TarockGame()
uri = daemon.register(tarock)
ns.register("example.tarock", uri)

print("Ready.")
daemon.requestLoop()
