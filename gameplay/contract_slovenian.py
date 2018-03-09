from cards import *

"""
For the basic type of bet: 3,2,1, etc.
"""
class slovenianGeneric:
  def __init__(self):
    self.talon = Pile()
    pass
  ## 
  def getCardValue(self,card):
    if   card.name == CardName.UNDEFINED:
      raise ValueError("Undefined card passed to getCardValue!")
    elif card.name == CardName.JACK:
      return 2.-2./3.
    elif card.name == CardName.CAVALIER:
      return 3.-2./3.
    elif card.name == CardName.QUEEN:
      return 4.-2./3.
    elif card.name == CardName.KING  or\
         card.name == CardName.PAGAT or\
         card.name == CardName.MONDE or\
         card.name == CardName.SKIS:
      return 5.-2./3.
    else:
      return 1./3.
  ## find top card in pile, return its index from original pile
  ## pretty inefficient, but probably okay
  def rankPile(self,pile):
    suitList,nameList = pile.getFlat()
    if CardName.PAGAT in nameList and\
       CardName.MONDE in nameList and\
       CardName.SKIS  in nameList:
      return nameList.index( CardName.PAGAT ) ## emperor trick
    #
    newPile = pile.copyPile()
    newPile.orderPile()
    if CardSuit.TRUMP in suitList:
      topCard = newPile.pile[0]
      return pile.pile.index( topCard ) ## trump card, already ordered
    else:
      leadSuit = pile.pile[0].suit
      suitList,nameList = newPile.getFlat()
      if leadSuit.name == CardSuit.HEART or\
         leadSuit.name == CardSuit.DIAMOND:
        ## check for reverse ordering of red suits
        topCard = newPile.pile[ suitList.index(leadSuit) ]
        if topCard.name.value > 22: ## face card, already ordered
          return pile.pile.index( topCard )
        else: ## find the cards of leading suit and return the last
          suitList.reverse()
          topCard = newPile.pile[ len(suitList) - 1 - suitList.index(leadSuit) ]
          return pile.pile.index( topCard )
      else:
        topCard = newPile.pile[ suitList.index(leadSuit) ]
        return pile.pile.index( topCard ) ## black card, already ordered
    pass

  def legalLead(self, hand, card):
    return True  #all cards are legal to lead under this contract

  def legalFollow(self, hand, card, trick):
    if card.suit == trick[0].suit: #followed suit
      return True
    else:
      suitList,nameList = hand.getFlat()
      if trick[0].suit in suitList: #should have followed suit
        return False
      elif card.suit == CardSuit.TRUMP: #trumped    
        return True
      elif CardSuit.TRUMP in suitList: #should have trumped
        return False
      else: # could not trump
        return True

