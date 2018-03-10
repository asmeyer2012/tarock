from cards import *

"""
Rules for the klop contract
"""
class klop:
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

  ## determine whether card would be the highest-ranking card if it is played to pile
  def beatTrick(self,pile,card):
    trick = pile.copyPile()
    trick.addCard(card)
    topidx = trick.rankPile()
    if topidx == len(pile):
      return True
    else:
      return False

  def legalLead(self, hand, card):
    # only illegal lead card is Pagat, unless it's your last card
    if (card.name.value == 0 and len(hand) > 1):
      return False
    else:
      return True

  def legalFollow(self, hand, card, trick):
    # is it the wrong suit?
    if card.suit != trick[0].suit:
      if sum(c.suit == trick[0].suit for c in hand) > 0:
        return False
      elif card.suit != CardSuit.TRUMP:
        if sum(c.suit == CardSuit.TRUMP for c in hand) > 0:
          return False

    # The suit is right, now check that the card wins if possible
    if beatTrick(trick, card):
      return True
    else:
      for c in hand:
        if c.suit == card.suit:
          if beatTrick(trick, c):
            return False

    # finally, a special case for the Pagat:
    if card.name == CardName.PAGAT:
      if sum(c.suit == CardSuit.TRUMP for c in hand) > 1:
        return False

    # if we get here, the card is ok
    return True
