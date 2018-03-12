import Pyro4
import time

class GameCommands:
  def __init__(self):
    self.idx = -1

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

#TODO: When someone leaves, let everyone know, and update idx's
  def leave(self):
    if self.idx >=0:
      tarock.leavetable(self.idx)
    else:
      print "You cannot leave before you arrive!\n\r"

  def broadcast(self, name, mess):
    tarock.broadcast(name, mess)

nameserver = Pyro4.locateNS()
tarockuri = nameserver.lookup("example.tarock")
tarock = Pyro4.Proxy(tarockuri)
