from enum import Enum
from itertools import cycle

"""
Contract Names and Values
"""
class ContractName(Enum):
  UNDEFINED = -1
  KLOP = 0
  THREE = 10
  TWO = 20
  ONE = 30
  SOLO_THREE = 40
  SOLO_TWO = 50
  SOLO_ONE = 60
  BEGGAR = 70
  SOLO_WITHOUT = 80
  OPEN_BEGGAR = 90
  COLOR_VALAT = 125
  VALAT = 250

class Announcements(Enum):
  TRULA = 0
  KINGS = 1
  PAGAT_ULTIMO = 2
  KING_ULTIMO = 3
  VALAT = 4

class Auction:
  def __init__(self, dealer, tablec, klop):
    self.dealer = dealer
    self.table = tablec
    self.livebidder = next(next(self.tablec))
    self.highbidder = None
    self.livebid = Contract.UNDEFINED
    self.compulsoryklop = klop
    for p in tablec:
      p.passed = False
    self.passes = 0
    self.done = False

  # returns True for legal bids, False for illegal bids
  def raisebid(self, player, bid):
    if player != self.livebidder or player.passed:
      return False
    elif not self.compulsoryklop:
      # TODO: How does precendence work again?
      if bid > self.livebid or (bid == self.livebid and False):
        if bid > Contract.THREE:
          self.livebidder = next(self.tablec)
          self.highbidder = player
          self.livebid = bid
          return True
        elif self.passes == 3:
          self.done = True
          return True
        else:
          return False
      else:
        return False
    else:
      #TODO: Precendence
      if bid > self.livebid or (bid == self.livebid and False):
        if bid > Contract.BEGGAR:
          self.livebidder = next(self.tablec)
          self.highbidder = player
          self.livebid = bid
          return True
        elif self.passes == 3 and bid == Contract.KLOP:
          self.done = True
          return True
        else:
          return False
      else:
        return False

  # Returns true for legal passes, False otherwise
  def passbid(self, player):
    if player == self.livebidder and self.passes < 3:
      self.livebidder = next(self.tablec)
      if player.passed:
        return True
      else:
        player.passed = True
        self.passes += 1
        if self.passes == 3 and self.livebid != Contract.UNDEFINED
          self.done = True
        return True
    else:
      return False

class Contract:
  def __init__(self,name):
    self.name = name
    self.announcements = list()
    self.kontra = 1
    pass

  def kontra():
    if self.kontra < 16:
      self.kontra *= 2
    else:
      print "Enough with the kontras already"
