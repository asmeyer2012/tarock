
from communication.menu import Menu

class Player:
  def __init__(self,name,server):
    self._name = name
    self._server = server
    self._score = 0
    self.Cleanup()

  def SetScore(self,score):
    self._score = score

  def GetScore(self):
    return self._score

  def Cleanup(self):
    self._handMenu = Menu(info=True)
    self._hand = {}       ## Card class objects, keys are Card.ShortName()
    self._tricks = {}     ## Card class objects won in tricks
    self._talonCards = [] ## track cards that came from talon

  ## add Card objects to hand when dealing or handling talon
  def AddToHand(self,card,fromTalon=False):
    self._handMenu.AddEntry( card.ShortName(), card.LongName())
    self._hand[ card.ShortName()] = card
    if fromTalon: ## keep track of which cards come from talon
      self._talonCards.append( card.ShortName())

  ## lay down cards after taking from talon
  def DiscardFromHand(self,req):
    card = self._hand[ req]
    self._handMenu.MaskEntry( card.ShortName())
    self._tricks[ req] = card
    self._server.ClientHook( self._name).PrintMessage(
      "you laid down {}".format( card.LongName()))
    self._server.BroadcastMessage("{} laid down a card".format( self._name))
    return len( self._tricks.keys()) ## used to determine change to announcements

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

  ## convert the hand from menu to info-only
  def HandToInfo(self):
    self._handMenu.SetToInfo()
    self._server.BuildMenu( self._name, 'hand')

  ## add cards to hand when dealing or handling talon
  def TakeTrick(self, trick):
    for card in trick.values():
      self._tricks[ card.ShortName()] = card

  def CardsInHand(self):
    return len( self._handMenu.keys())

  def ScoreTricks(self, contract):
    cardValueSum = 0
    for card in self._tricks.values():
      cardValueSum += contract.CardValue( card)
    return cardValueSum

