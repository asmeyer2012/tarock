from enum import Enum

class Stage(Enum):
  INITIATE = -1
  DEAL = 0
  BID = 1
  RAISEBID = 2
  KING = 3
  ANNOUNCEMENTS = 4
  KONTRA = 5
  TALON = 6
  LEADTRICK = 7
  FOLLOWTRICK = 8
  SCORE = 9
  CONCLUDE = 10
