
from communication.menu import Menu

class Player:
  def __init__(self,name,server):
    self._name = name
    self._server = server
    self._score = 0
    #self._radliRemaining = 0
    #self._radliFinished = 0
    self._handMenu = Menu(info=True)
    self._hand = {}      ## Card class objects, keys are Card.ShortName()
    self._talonHand = {} ## Cards from talon that are assigned to Player
    #self._tricks = {} ## Card class objects won in tricks

  def SetScore(self,score):
    self._score = score

  def GetScore(self):
    return self._score

  #def AddRadli(self):
  #  self._radliRemaining += 1

  #def FinishRadli(self):
  #  self._radliFinished += 1
  #  self._radliRemaining -= 1

  ## add cards to hand when dealing or handling talon
  def AddToHand(self,card,fromTalon=False):
    self._handMenu.AddEntry( card.ShortName(), card.LongName())
    if fromTalon: ## keep track of which cards come from talon
      self._talonHand[ card.ShortName()] = card
    else:
      self._hand[ card.ShortName()] = card

  def MenuMask(self, tag):
    if tag == 'hand':
      return self._handMenu._mask

  def GetMenu(self, tag):
    if tag == 'hand':
      return self._handMenu

  ## convert the hand from info-only to menu
  def HandToMenu(self):
    self._handMenu.SetToMenu()
    self._server.BuildMenu( self._name, 'hand')

  ### add cards to hand when dealing or handling talon
  #def AddToTricks(self,card):
  #  self._tricks[ card.ShortName()] = card

  ### when a card is played or laid down, just mask rather than remove
  #def MaskCard(self,card):
  #  self._handMenu.MaskEntry( card.ShortName())

