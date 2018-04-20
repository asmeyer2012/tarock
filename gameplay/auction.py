from enum import Enum

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

class Contract:
  def __init__(self,name):
    self.name = name
    self.announcements = list()
    self.kontra = 1
    self.compulsoryKlop = False # Flag for next hand
    pass

  def kontra():
    if self.kontra < 16:
      self.kontra *= 2
    else:
      print "Enough with the kontras already"
