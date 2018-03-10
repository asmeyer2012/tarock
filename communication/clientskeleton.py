import Pyro4
import time

class GameCommands:
  def __init__(self):
    self.idx = -1

  def register(self, name):
    self.idx = tarock.newplayer(name)
    print "You have been registered as " + tarock.printplayer(self.idx) + '\r'
    if self.idx > 0:
      mess = "Other players are:\n\r"
      for p in range (self.idx):
        mess += tarock.printplayer(p)
        mess += '\r'
      print mess
    else:
      print "No other players\n\r"

#TODO: Let everyone know when someone deals
  def deal(self):
    if tarock.getplayers() > 3:
      tarock.deal()
      print "Hand dealt\n\r"
    else:
      print "Not enough players to deal yet\n\r"

  def showhand(self):
    if self.idx >= 0:
      print "Here is your hand:\n\r"
      print(tarock.printHand(self.idx))
    else:
      print "You must register first\n\r"

#TODO: When someone leaves, let everyone know, and update idx's
  def leave(self):
    if self.idx >=0:
      tarock.leavetable(self.idx)
    else:
      print "You cannot leave before you arrive!\n\r"

nameserver = Pyro4.locateNS()
tarockuri = nameserver.lookup("example.tarock")
tarock = Pyro4.Proxy(tarockuri)
