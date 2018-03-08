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
  SOLO THREE = 40
  SOLO TWO = 50
  SOLO ONE = 60
  BEGGAR = 70
  SOLO WITHOUT = 80
  OPEN BEGGAR = 90
  COLOR VALAT = 125
  VALAT = 250

class Announcements(Enum):
  TRULA = 0
  KING ULTIMO = 1
  KINGS = 2
  PAGALT ULTIMO = 3
  VALAT = 4

class Contract:
  def __init__(self,name):
    self.name = name
    self.announcements = list()
    self.contra = 1
    pass
