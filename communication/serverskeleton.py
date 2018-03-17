# KLabe attempt at a Python class for tracking the game
import Pyro4
import sys
sys.path.insert(0, '../')
from gameplay.deck_slovenian import *
from gameplay.cards import *
from gameplay.player import *
from gameplay.orderofplay import *
from gameplay.auction import *
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
    self.auction = None
    self.compulsoryklop = False

  def newplayer(self, name):
    player = Player(name)
    curi = ns.lookup("example.client.{0}".format(name))
    player.client = Pyro4.Proxy(curi)
    self.broadcast("Player {0} arrived.".format(name))
    self.players.append(player)
    if len(self.players) <= 4:
      self.table.append(player)
    if len(self.players) == 4 and self.stage == Stage.INITIATE:
      self.stage = Stage.DEAL
      self.broadcast("Ready for {0} to deal".format(self.players[self.dealeridx].name))
    return len(self.players) - 1

  def leavetable(self, idx):
    self.broadcast("{0} is leaving.".format(self.players[idx].name))
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
    if self.stage == Stage.DEAL and idx == self.dealeridx:
      deck = slovenianDeck()
      pile = Pile()
      pile.addCards( deck.getShuffled() )
      for x in range(12):
        for p in range(4):
          c1 = pile.takeCard()
          self.players[p].hand.putCard(c1)
      self.stage = Stage.BID
      self.broadcast("Hand dealt!")
      self.auction = Auction(self.players[idx], self.table, self.compulsoryklop)
      self.broadcast("{0} has the first bid at Two".format(self.auction.livebidder.name))
    else:
      self.players[idx].client.writegame("Cannot deal from this state")

  #Internal function
  def king(self):
    if self.auction.callking():
      self.stage = Stage.KING
      self.broadcast("Call a king")
    else:
      self.stage = Stage.ANNOUNCEMENTS
      self.broadcast("Time for announcements")

  def raisebid(self, idx, bid):
    if not self.stage == Stage.BID:
      if not self.stage == Stage.RAISEBID:
        self.players[idx].client.writegame("No auction now")
        return
    if not self.players[idx] == self.auction.livebidder:
      self.players[idx].client.writegame("You are not the current bidder")
    else:
      if self.stage == Stage.BID:
        if not self.auction.raisebid(self.players[idx], bid):
          self.players[idx].client.writegame("Not a legal bid")
        if self.auction.done:
          self.auction.livebidder = self.auction.highbidder
          self.stage == Stage.RAISEBID
          self.broadcast("{0} has the bid at {1}.  Raise bid?".format(self.auction.highbidder.name, self.auction.livebid.name))
      elif self.stage == Stage.RAISEBID:
        if not self.auction.raisebid(self.players[idx], bid):
          self.players[idx].client.writegame("Not a legal raise bid")
        else:
          self.king()
      else:
        self.players[idx].client.writegame("Cannot bid at this time")

  def passbid(self, idx):
    if not self.stage == Stage.BID:
      if not self.stage == Stage.RAISEBID:
        self.players[idx].client.writegame("No auction now")
        return
    if not self.players[idx] == self.auction.livebidder:
      self.players[idx].client.writegame("You are not the current bidder")
    else:
      if self.stage == Stage.BID:
        if not self.auction.passbid(self.players[idx]):
          self.players[idx].client.writegame("You cannot pass!")
        if self.auction.done:
          self.auction.livebidder = self.auction.highbidder
          self.stage = Stage.RAISEBID
          self.broadcast("{0} has the bid at {1}.  Raise bid?".format(self.auction.highbidder.name, self.auction.livebid.name))
      elif self.stage == Stage.RAISEBID:
        self.king()
      else:
        self.players[idx].client.writegame("No passing at this time")
  

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

tarock = TarockGame()
uri = daemon.register(tarock)
ns.register("example.tarock", uri)

print("Ready.")
daemon.requestLoop()
