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
  KING_ULTIMO = 1
  KINGS = 2
  PAGALT_ULTIMO = 3
  VALAT = 4

class Contract:
  def __init__(self,name):
    self.name = name
    self.announcements = list()
    self.contra = 1
    pass
