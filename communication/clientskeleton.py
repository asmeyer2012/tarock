import Pyro4
import sys
sys.path.insert(0,'../')
from interface.interface import *
import threading
import curses
import os
import sys

@Pyro4.expose
class GameCommands:
  def __init__(self,name):
    self.idx = -1
    self.name = name
    self.interface = None

  def register(self, name):
    if self.idx != -1:
      mess = "You are already registered!"
    else:
      self.idx = tarock.newplayer(name)
      if self.idx >= 0:
        mess = "You have been registered as " + tarock.printplayer(self.idx)
      else:
        mess = "You cannot register at this time"
    return mess

  # This function is called by the server when someone leaves
  def updateidx(self, idx):
    if self.idx > idx:
      self.idx -= 1

  def printPlayers(self):
    if self.idx > -1:
      mess = "Players are: "
      for p in range (self.idx+1):
        if p != 0:
          mess += ', '
        mess += tarock.printplayer(p)
      mess += '.'
      return mess
    else:
      mess = "No players\n\r"
      return mess

  def deal(self):
    mess = tarock.deal()
    return mess

  def handlen(self):
    return tarock.handlen(self.idx)

  def printCard(self, i):
    if self.idx >= 0:
      return tarock.printCard(self.idx, i)
    else:
      return "You must register first"

  def leave(self):
    if self.idx >=0:
      tarock.leavetable(self.idx)
    else:
      print "You cannot leave before you arrive!\n\r"
    daemon.shutdown()

  def test(self):
    return "test"

  def broadcast(self, name, mess):
    tarock.broadcast(name, mess)

  def writemsg(self, name, mess):
    self.interface.writemsg(name, mess)

  def writegame(self, mess):
    self.interface.gmWin.addLine(mess)

def listen():
  daemon.requestLoop()


## MAIN
playerName = sys.argv[1]
stdscr = curses.initscr()

## Create a client object and register it
gc = GameCommands(playerName)
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(gc)
ns.register("example.client.{0}".format(playerName), uri)

## Now that we're registered, create a command window to use
gc.interface = CommandWindow(playerName)

## Connect to the remote Tarock Server
tarockuri = ns.lookup("example.tarock")
tarock = Pyro4.Proxy(tarockuri)

## Launch a new thread to listen to the interface
t = threading.Thread(target = listen)
t.start()

## Start running the interface
curses.wrapper(gc.interface.idleLoop)
